import bpy
from bpy.types import Object as BObject, Action

from . import o_motion
from .o_motion import ActionSet
from .o_model import ModelData
from .o_keyframes import ShapeKeyframeEvaluator

from ..dotnet import SA3D_Modeling
from ..exceptions import UserException, SAIOException


class ShapeActionCollection:

    action: Action
    slots: dict[BObject, bpy.types.ActionSlot]
    motion_name: str

    def __init__(self):
        self.action = None
        self.slots = {}
        self.motion_name = ""


def _find_has_mesh_children(target: BObject):
    for child in target.children:
        if child.type == 'MESH' or _find_has_mesh_children(child):
            return True
    return False


def check_is_shape_motion_viable(armature_object: BObject):
    for child in armature_object.children:
        if _find_has_mesh_children(child):
            raise UserException(
                f"Object {child.name} itself has meshes in its child"
                " hierarchy! Not valid for shape motions!")


class ShapeActionCollector:

    target: BObject
    frame: int
    result: ShapeActionCollection

    def __init__(
            self,
            target: BObject,
            frame: int):

        self.target = target
        self.frame = frame
        self.result = None

        if target.type == 'ARMATURE':
            check_is_shape_motion_viable(target)

    def _setup(self):
        self.result = ShapeActionCollection()

    def _should_be_skipped(self, obj: BObject):
        from ..utility.general import get_armature_modifier
        return (
            obj.type != 'MESH'
            or getattr(obj.data, "shape_keys", None) is None
            or get_armature_modifier(obj) is not None
        )

    def _find_action(self, model: BObject) -> ActionSet | None:
        if self._should_be_skipped(model):
            return None


        action = ActionSet.from_data(
            model.data.shape_keys,
            self.frame,
            ignore_selected=False
        )

        if action is not None:
            self.result.action = action.action
            self.result.slots[model] = action.slot
            return True
        
        return False

    def _find_slot(self, obj: bpy.types.Object):
        shape_keys: bpy.types.Key = getattr(obj.data, "shape_keys", None)
        if shape_keys is None:
            return None
        
        if shape_keys.animation_data.action == self.result.action:
            return shape_keys.animation_data.action_slot
        
        for track in shape_keys.animation_data.nla_tracks:
            for strip in track.strips:
                if strip.action == self.result.action:
                    return strip.action_slot
            
        # If none is assigned anywhere, try to get one with the name of the object
        return self.result.action.slots.get(f"KE{obj.name}")

    def _collect_armature(self):
        for child in self.target.children:
            if child.parent_type == 'BONE' and self._find_action(child):
                break

        if self.result.action is None:
            return

        for child in self.target.children:
            if child.parent_type != 'BONE' or self._should_be_skipped(child) or child in self.result.slots:
                continue

            slot = self._find_slot(child)
            if slot is not None:
                self.result.slots[child] = slot

    def collect(self):
        self._setup()

        if self.target.type == 'ARMATURE':
            self._collect_armature()
        elif not self._should_be_skipped(self.target):
            self._find_action(self.target)

        if self.result.action is None:
            return None

        self.result.motion_name = self.result.action.name
        return self.result

    @staticmethod
    def collect_shape_actions(target: BObject, frame: int):
        collector = ShapeActionCollector(target, frame)
        return collector.collect()


class ShapeMotionEvaluator:

    _model_data: ModelData
    _node_map: dict[bpy.types.PoseBone, int]
    _shape_evaluators: dict[BObject, ShapeKeyframeEvaluator]
    _context: bpy.types.Context
    _normal_mode: str

    _action: bpy.types.Action
    _slots: dict[BObject, bpy.types.ActionSlots]
    _depsgraph: bpy.types.Depsgraph

    _start: int
    _end: int
    _duration: int
    _output: any

    def __init__(
            self,
            model_data: ModelData,
            context: bpy.types.Context,
            normal_mode: str):

        self._model_data = model_data
        self._shape_evaluators = {}
        self._context = context
        self._normal_mode = normal_mode
        self._action = None
        self._slots = None

        if self._model_data.node_data.armature_object is not None:
            self._node_map = {}
            self._setup_node_map()
        else:
            self._node_map = None

    def _evaluate_time(self):
        self._start, self._end = o_motion.get_frame_range([
            ActionSet(self._action, slot) 
            for slot in self._slots.values()
        ])
        
        self._duration = self._end - self._start

    def _setup_node_map(self):
        index = 0
        for source in self._model_data.node_data.node_mapping.keys():
            if not source.bone.saio_node.no_morph:
                self._node_map[source.name] = index
                index += 1

    def _setup_output(self, name: str):

        node_count = 1 if self._node_map is None else len(self._node_map)

        self._output = SA3D_Modeling.MOTION()
        self._output.NodeCount = node_count
        self._output.Label = name

    def _convert_slot(self, slot: bpy.types.ActionSlot, obj: BObject, index: int):
        channelbag = self._action.layers[0].strips[0].channelbag(slot)
        if channelbag is None:
            return

        if obj not in self._shape_evaluators:
            modelmesh = self._model_data.meshes[obj]
            evaluator = ShapeKeyframeEvaluator(modelmesh, self._normal_mode)
            self._shape_evaluators[obj] = evaluator
        else:
            evaluator = self._shape_evaluators[obj]


        keyframes = evaluator.evaluate(
            self._action.name,
            channelbag,
            self._depsgraph,
            self._start,
            self._duration
        )
        self._output.Keyframes.Add(index, keyframes)

    def _evaluate_for_armature(self):
        bone_model = self._model_data.node_data.bone_models
        for bone_name, objects in bone_model.items():
            if len(objects) > 1:
                raise UserException(
                    f"Bone {bone_name} Has more than one mesh!")

            obj, _ = objects[0]
            if (obj.parent_bone not in self._node_map
                    or obj not in self._slots):
                continue

            self._convert_slot(
                self._slots[obj],
                obj,
                self._node_map[obj.parent_bone])

    def evaluate(self, slot: ShapeActionCollection):

        self._depsgraph = self._context.evaluated_depsgraph_get()
        self._action = slot.action
        self._slots = slot.slots
        self._evaluate_time()
        self._setup_output(slot.motion_name)

        if self._normal_mode == 'TYPED':
            self._output.ManualKeyframeTypes = SA3D_Modeling.KEYFRAME_ATTRIBUTES.Normal

        if self._node_map is not None:
            self._evaluate_for_armature()
        else:
            if len(self._slots) > 1:
                raise SAIOException("More than one action to convert")

            for obj, slot in self._slots.items():
                self._convert_slot(slot, obj, 0)

        return self._output
