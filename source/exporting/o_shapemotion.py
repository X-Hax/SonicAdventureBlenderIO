import bpy
from bpy.types import Object as BObject, Action

from . import o_motion
from .o_model import ModelData
from .o_mesh import ModelMesh
from .o_keyframes import ShapeKeyframeEvaluator

from ..exceptions import UserException


class ShapeActionCollection:

    actions: dict[BObject, Action]
    motion_name: str

    def __init__(self):
        self.actions = {}
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

    starter_action: Action

    result: ShapeActionCollection

    def __init__(
            self,
            target: BObject,
            frame: int):

        self.target = target
        self.frame = frame
        self.starter_action = None
        self.result = None

        if target.type == 'ARMATURE':
            check_is_shape_motion_viable(target)

    def _setup(self):
        self.starter_action = None
        self.result = ShapeActionCollection()

    def _should_be_skipped(self, object: BObject):
        from ..utility.general import get_armature_modifier
        return (
            object.type != 'MESH'
            or object.data.shape_keys is None
            or get_armature_modifier(object) is not None
        )

    def _find_starter_action(self, model: BObject):
        if self._should_be_skipped(model):
            return None

        action = o_motion.get_action(
            model.data.shape_keys,
            self.frame,
            ignore_selected=False)

        if action is None:
            return None

        elif not action.name.endswith("_" + model.name):
            raise UserException(
                f"Target Action \"{action.name}\" of object"
                f" \"{model.name}\" does not match naming!\n"
                "Has to end with objectname\n"
                f"(e.g. \"ExampleActionName_{model.name}\")")

        return action

    def _find_armature_starter_action(self):
        for child in self.target.children:
            action = self._find_starter_action(child)

            if action is not None:
                self.starter_action = action
                self.result.motion_name = action.name[:-(1 + len(child.name))]
                return

    def _collect_armature(self):
        self._find_armature_starter_action()

        if self.starter_action is None:
            return

        for child in self.target.children:
            if child.parent_type != 'BONE' or self._should_be_skipped(child):
                continue

            try:
                action = bpy.data.actions[
                    f"{self.result.motion_name}_{child.name}"]
            except KeyError:
                continue

            self.result.actions[child] = action

    def _collet_object(self):
        action = self._find_starter_action(self.target)
        if action is not None:
            self.result.actions[self.target] = action
            self.result.motion_name = action.name

    def collect(self):
        self._setup()

        if self.target.type == 'ARMATURE':
            self._collect_armature()
        else:
            self._collet_object()

        if len(self.result.actions) == 0:
            return None

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

    _actions: dict[BObject, Action]
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

        if self._model_data.node_data.armature_object is not None:
            self._node_map = {}
            self._setup_node_map()
        else:
            self._node_map = None

    def _evaluate_time(self):
        self._start, self._end = o_motion.get_frame_range(
            self._actions.values())
        self._duration = self._end - self._start

    def _setup_node_map(self):
        index = 0
        for source in self._model_data.node_data.node_mapping.keys():
            if not source.bone.saio_node.no_morph:
                self._node_map[source.name] = index
                index += 1

    def _setup_output(self, name: str):
        from SA3D.Modeling.ObjectData.Animation import Motion

        node_count = 1 if self._node_map is None else len(self._node_map)

        self._output = Motion(self._duration, node_count)
        self._output.Label = name

    def _convert_action(self, action: Action, object: BObject, index: int):
        if object not in self._shape_evaluators:
            modelmesh = self._model_data.meshes[object]
            evaluator = ShapeKeyframeEvaluator(modelmesh, self._normal_mode)
            self._shape_evaluators[object] = evaluator
        else:
            evaluator = self._shape_evaluators[object]

        keyframes = evaluator.evaluate(
            action,
            self._depsgraph,
            self._start,
            self._duration)
        self._output.Keyframes.Add(index, keyframes)

    def _evaluate_for_armature(self):
        bone_model = self._model_data.node_data.bone_models
        for bone_name, objects in bone_model.items():
            if len(objects) > 1:
                raise UserException(
                    f"Bone {bone_name} Has more than one mesh!")

            object, _ = objects[0]
            if (object.parent_bone not in self._node_map
                    or object not in self._actions):
                continue

            self._convert_action(
                self._actions[object],
                object,
                self._node_map[object.parent_bone])

    def evaluate(self, actions: ShapeActionCollection):

        self._depsgraph = self._context.evaluated_depsgraph_get()
        self._actions = actions.actions
        self._evaluate_time()
        self._setup_output(actions.motion_name)

        if self._normal_mode == 'TYPED':
            from SA3D.Modeling.ObjectData.Animation import AnimationAttributes
            self._output.ManualType = AnimationAttributes.Normal

        if self._node_map is not None:
            self._evaluate_for_armature()
        else:
            if len(self._actions) > 1:
                raise Exception("More than one action to convert")

            for object, action in self._actions.items():
                self._convert_action(action, object, 0)

        return self._output
