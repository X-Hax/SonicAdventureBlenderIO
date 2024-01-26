import bpy
from bpy.types import Object as BObject

from .o_shapemotion import (
    check_is_shape_motion_viable,
    ShapeActionCollection,
    ShapeMotionEvaluator
)
from .o_model import ModelData

from ..utility import camera_utils
from ..utility.anim_parameters import AnimParameters
from ..exceptions import UserException

class CutInfo:

    context: bpy.types.Context
    scene: bpy.types.Scene
    index: int
    particles: list[BObject]
    models: dict[BObject, ModelData]
    anim_parameters: AnimParameters
    shape_motion_evaluators: dict[BObject, ShapeMotionEvaluator]

    entries: list[BObject]
    duration: int

    temp_actions: list[bpy.types.Action]
    output_actions: dict[BObject, bpy.types.Action]
    output_shape_actions: dict[BObject, ShapeActionCollection]
    action_setup_dict: dict[bpy.types.FCurve, any]

    camera_setup: camera_utils.CameraSetup
    camera_actions: camera_utils.CameraActionSet

    motions: dict[BObject, any]
    shape_motions: dict[BObject, any]
    camera_motion: any

    def __init__(
            self,
            context: bpy.types.Context,
            scene: bpy.types.Scene,
            index: int,
            models: dict[BObject, ModelData],
            anim_parameters: AnimParameters,
            shape_motion_evaluators: dict):

        self.context = context
        self.scene = scene
        self.index = index
        self.entries = []
        self.particles = []
        self.anim_parameters = anim_parameters
        self.models = models
        self.shape_motion_evaluators = shape_motion_evaluators

        self.duration = scene.frame_end - scene.frame_start

        self.temp_actions = []
        self.output_actions = {}
        self.output_shape_actions = {}
        self.action_setup_dict = {}

        self.camera_setup = camera_utils.CameraSetup.get_setup(
            self.scene.camera)

        if self.camera_setup is None:
            raise UserException(
                f"Camera setup in scene {self.scene.name} is invalid!")

        self.camera_actions = None

        self.motions = {}
        self.shape_motions = {}
        self.camera_motion = None

    @property
    def framecount(self):
        # a scene from 0 to 1 has 2 frames, but 1 - 0 is 1, so we gotta add 1
        return self.duration + 1

    def _setup_motion_scene(self):

        self.context.window.scene = self.scene
        self.scene.frame_current = self.scene.frame_start

    ######################################################################

    def _is_animated(self, animdata):
        if animdata is None:
            return False

        stripcount = sum([
            len(track.strips)
            for track
            in animdata.nla_tracks]
        )

        return stripcount > 0

    def _get_matching_action(self, anim: bpy.types.AnimData):

        tracks = [track for track in anim.nla_tracks if len(track.strips) > 0]
        if len(tracks) != 1:
            return None
        track = tracks[0]

        matching_strip = None
        for strip in track.strips:
            if (strip.frame_start == self.scene.frame_start
                    and strip.frame_end == self.scene.frame_end):
                matching_strip = strip
                break

        if matching_strip is None or matching_strip.type != 'CLIP':
            return None

        frame_range = matching_strip.action.frame_range
        frame_length = frame_range[1] - frame_range[0]
        if (frame_length == self.duration
                and len(matching_strip.modifiers) == 0
                and matching_strip.scale == 1):
            return matching_strip.action

        return None

    def _setup_action(self, animdata, name, on_create, ensure_action=False):
        if not self._is_animated(animdata) and not ensure_action:
            return None

        action = self._get_matching_action(animdata)

        if action is None:
            action = bpy.data.actions.new(
                f"SAIO_{self.scene.name}_{name}")
            self.temp_actions.append(action)

            on_create(action)

        return action

    ######################################################################

    def _setup_temp_armature_action(
            self,
            action: bpy.types.Action,
            obj: BObject):

        for bone in obj.pose.bones:

            def create_curve(field, length):
                for i in range(length):
                    curve = action.fcurves.new(
                        f"pose.bones[\"{bone.name}\"].{field}",
                        index=i,
                        action_group=bone.name)
                    self.action_setup_dict[curve] = (bone, field, i)

            create_curve("location", 3)
            create_curve("scale", 3)

            if bone.rotation_mode == 'QUATERNION':
                create_curve("rotation_quaternion", 4)
            else:
                create_curve("rotation_euler", 3)

    def _setup_temp_object_action(
            self,
            action: bpy.types.Action,
            obj: BObject,
            no_scale: bool = False):

        def create_curve(field, length):
            for i in range(length):
                curve = action.fcurves.new(
                    field,
                    index=i,
                    action_group="transforms")
                self.action_setup_dict[curve] = (obj, field, i)

        create_curve("location", 3)

        if obj.rotation_mode == 'QUATERNION':
            create_curve("rotation_quaternion", 4)
        else:
            create_curve("rotation_euler", 3)

        if not no_scale:
            create_curve("scale", 3)


    def _setup_temp_target_action(self, action: bpy.types.Action, obj):

        def create_curve(field, index):
            curve = action.fcurves.new(
                field,
                index=index,
                action_group="transforms")
            self.action_setup_dict[curve] = (obj, field, index)

        for i in range(3):
            create_curve("location", i)
        create_curve("rotation_euler", 2)

    def _setup_temp_fov_action(self, action: bpy.types.Action, obj):
        action.id_root = 'CAMERA'
        curve = action.fcurves.new(
            "lens",
            action_group="camera")
        self.action_setup_dict[curve] = (obj, "lens", None)

    ######################################################################

    def _get_shape_action(self, obj: BObject):
        if obj.type != 'MESH':
            return None

        from ..utility.general import get_armature_modifier
        if get_armature_modifier(obj) is not None:
            return None

        keys: bpy.types.Key = obj.data.shape_keys
        if keys is None or keys.animation_data is None:
            return None

        target_track = None
        for track in keys.animation_data.nla_tracks:
            if len(track.strips) == 0:
                continue

            if target_track is not None:
                raise UserException(
                    f"Object {obj.name} has multiple NLA tracks on its"
                    " shape data!")

            target_track = track

        if target_track is None:
            return None

        target_strip = None
        for strip in target_track.strips:
            if (strip.frame_start == self.scene.frame_start
                    and strip.frame_end == self.scene.frame_end):
                target_strip = strip
                continue

            if not (strip.frame_start > self.scene.frame_end
                    or strip.frame_end < self.scene.frame_start):
                raise UserException(
                    "All shape actions on an nla track have to fit"
                    " exactly onto the scene they are played in! Object"
                    f" {obj.name} does not comply!")

        if target_strip is None or target_strip.type != 'CLIP':
            return None

        frame_range = target_strip.action.frame_range
        frame_length = frame_range[1] - frame_range[0]
        if (frame_length != self.duration
                or len(target_strip.modifiers) != 0
                or target_strip.scale != 1):

            raise UserException(
                f"Shape action {target_strip.action.name}"
                f" on object {obj.name} does not match with its strip"
                " or is not \"vanilla\"!")

        return target_strip.action

    def _collect_shape_actions(self, entry: BObject):
        shape_actions = ShapeActionCollection()

        if entry.type == 'ARMATURE':
            for child in entry.children:
                if child.parent_type != 'BONE':
                    continue
                action = self._get_shape_action(child)
                if action is not None:
                    shape_actions.actions[child] = action

            if len(shape_actions.actions) > 0:
                check_is_shape_motion_viable(entry)

        else:
            action = self._get_shape_action(entry)
            if action is not None:
                shape_actions.actions[entry] = action

        if len(shape_actions.actions) > 0:
            shape_actions.name = f"Event{self.index}_{entry.name}_Shape"
            self.output_shape_actions[entry] = shape_actions

    def _prepare_entry_actions(self):

        for entry in self.entries:
            if entry.type != 'ARMATURE' and len(entry.children) > 0:
                continue

            # Node animation

            def create(x):
                if entry.type == 'ARMATURE':
                    self._setup_temp_armature_action(x, entry)
                else:
                    self._setup_temp_object_action(x, entry)

            action = self._setup_action(
                entry.animation_data,
                f"Scene{self.index:02}_{entry.name}",
                create)

            if action is not None:
                self.output_actions[entry] = action

            self._collect_shape_actions(entry)

    def _prepare_particle_actions(self):

        for particle in self.particles:

            action = self._setup_action(
                particle.animation_data,
                particle.name,
                lambda x: self._setup_temp_object_action(x, particle))

            if action is not None:
                self.output_actions[particle] = action

    def _prepare_camera_actions(self):

        camera_action = self._setup_action(
            self.camera_setup.camera.animation_data,
            "camera",
            lambda x: self._setup_temp_object_action(
                x, self.camera_setup.camera, True),
            True)

        target_action = self._setup_action(
            self.camera_setup.target.animation_data,
            "target",
            lambda x: self._setup_temp_target_action(
                x, self.camera_setup.target),
            True)

        fov_action = self._setup_action(
            self.camera_setup.camera_data.animation_data,
            "fov",
            lambda x: self._setup_temp_fov_action(
                x, self.camera_setup.camera_data),
            True)

        self.camera_actions = camera_utils.CameraActionSet(
            camera_action,
            target_action,
            fov_action)

    ######################################################################

    def _eval_action_keyframes(self):
        if len(self.action_setup_dict) == 0:
            return

        for i in range(self.framecount):
            self.context.view_layer.update()

            for curve, params in self.action_setup_dict.items():
                value = getattr(params[0], params[1])
                if params[2] is not None:
                    value = value[params[2]]
                curve.keyframe_points.insert(i, value).interpolation = 'LINEAR'

            self.scene.frame_current += 1

    def _convert_actions(self):
        from .o_motion import convert_to_node_motion, convert_to_camera_motion

        self.camera_motion = convert_to_camera_motion(
            self.camera_setup,
            self.camera_actions,
            f"Scene{self.index:02}_Camera",
            self.anim_parameters
        )

        for obj, action in self.output_actions.items():
            self.motions[obj] = convert_to_node_motion(
                obj,
                False,
                action.fcurves,
                action.frame_range,
                action.name,
                self.anim_parameters
            )

        if len(self.output_shape_actions) > 0:

            for obj, actions in self.output_shape_actions.items():
                if obj not in self.shape_motion_evaluators:
                    evaluator = ShapeMotionEvaluator(
                        self.models[obj],
                        self.context,
                        'NONE')
                    self.shape_motion_evaluators[obj] = evaluator
                else:
                    evaluator = self.shape_motion_evaluators[obj]

                self.shape_motions[obj] = evaluator.evaluate(actions)

    def _cleanup(self):
        for action in self.temp_actions:
            bpy.data.actions.remove(action)

    def evaluate_motions(self):
        self._setup_motion_scene()

        self._prepare_entry_actions()
        self._prepare_camera_actions()
        self._prepare_particle_actions()

        self._eval_action_keyframes()

        self._convert_actions()
        self._cleanup()
