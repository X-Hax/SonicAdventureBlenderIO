import bpy
import math

from .i_keyframes import (
    TransformKeyframeProcessor,
    ShapeKeyframeProcessor
)
from . import i_matrix
from ..utility.camera_utils import CameraActionSet, CameraSetup
from ..exceptions import UserException


class ObjectMotionProcessor:

    _shape_motion: bool

    _motion: any
    '''Source motion'''

    _bobject: bpy.types.Object
    '''Target object'''

    _bonemap: list[str]

    def __init__(self, force_sort_bones: bool = False):

        self._shape_motion = False
        self._motion = None
        self._bobject = None
        self._bonemap = []
        self._force_sort_bones = force_sort_bones

    def _verify(self):
        if self._bobject is None:
            raise Exception("No object set!")
        elif self._motion is None:
            raise Exception("No motion set!")

        elif self._bobject.type == "ARMATURE":

            from ..utility import bone_utils
            self._bonemap = bone_utils.get_bone_map(
                self._bobject, self._force_sort_bones, self._shape_motion)

        elif (self._motion.Keyframes.Count > 1
              or not self._motion.Keyframes.ContainsKey(0)):
            raise UserException("Animation requires armature!")

        elif len(self._bobject.children) > 0:
            raise UserException((
                "Target has children! Can only apply this animation"
                " to armatures or standalone objects"))

    def process(self, motion, object: bpy.types.Object):
        self._motion = motion
        self._bobject = object
        self._bonemap.clear()
        self._verify()

        return None


class NodeMotionProcessor(ObjectMotionProcessor):

    _action: bpy.types.Action
    '''Output action'''

    _kf_processor: TransformKeyframeProcessor

    def __init__(
            self,
            rotation_mode: str,
            quaternion_conversion_deviation: float,
            force_sort_bones: bool = False):
        super().__init__(force_sort_bones)

        self._action = None

        self._kf_processor = TransformKeyframeProcessor(
            rotation_mode=rotation_mode,
            rotate_zyx=False,
            quaternion_conversion_deviation=quaternion_conversion_deviation
        )

    def _verify(self):
        super()._verify()

        if not self._motion.IsNodeMotion:
            raise Exception("Motion is not a node motion")

    def _create_action(self):
        self._action = bpy.data.actions.new(self._motion.Label)
        self._kf_processor.action = self._action

    def _process_armature_motion(self):

        for node_keyframes in self._motion.Keyframes:
            bone_name = self._bonemap[node_keyframes.Key]
            bone = self._bobject.pose.bones[bone_name]

            local_position, rotation_matrix = i_matrix.get_bone_transforms(
                bone)
            rotation_matrix.invert()

            self._kf_processor.rotate_zyx = bone.bone.saio_node.rotate_zyx
            self._kf_processor.group = bone.name
            self._kf_processor.path_prefix = f"pose.bones[\"{bone.name}\"]."

            bone.rotation_mode = \
                self._kf_processor.process_transform_keyframes(
                    node_keyframes.Value,
                    bone.rotation_mode,
                    local_position,
                    rotation_matrix)

    def _process_object_motion(self):

        self._kf_processor.group = "Object Transforms"
        self._kf_processor.path_prefix = ""
        self._kf_processor.rotate_zyx = self._bobject.saio_node.rotate_zyx

        self._bobject.rotation_mode = \
            self._kf_processor.process_transform_keyframes(
                self._motion.Keyframes[0],
                self._bobject.rotation_mode)

    def process(self, motion, object: bpy.types.Object):
        super().process(motion, object)

        self._create_action()

        if self._bobject.type == "ARMATURE":
            self._process_armature_motion()
        else:
            self._process_object_motion()

        return self._action

    @staticmethod
    def process_motion(
            motion: any,
            object: bpy.types.Object,
            force_sort_bones: bool,
            rotation_mode: str,
            quaternion_conversion_deviation: float):

        processor = NodeMotionProcessor(
            rotation_mode,
            quaternion_conversion_deviation,
            force_sort_bones)

        return processor.process(motion, object)


class ShapeMotionProcessor(ObjectMotionProcessor):

    _processors: dict[bpy.types.Object, ShapeKeyframeProcessor]

    _actions: dict[bpy.types.Object, bpy.types.Action]
    '''Output'''

    _optimize: bool

    def __init__(self, optimize: bool, force_sort_bones: bool = False):
        super().__init__(force_sort_bones)

        self._processors = {}
        self._actions = None
        self._shape_motion = True
        self._optimize = optimize

    def _verify(self):
        super()._verify()

        if not self._motion.IsShapeMotion:
            raise Exception("Motion is not a shape motion")

    def _convert(
            self,
            keyframes,
            object: bpy.types.Object,
            last_frame_number: int):

        action = bpy.data.actions.new(
            f"{self._motion.Label}_{object.data.name}")
        action.id_root = "KEY"

        if object in self._processors:
            processor = self._processors[object]
        else:
            processor = ShapeKeyframeProcessor(object, self._optimize)
            self._processors[object] = processor

        processor.process(keyframes, action, last_frame_number)
        self._actions[object] = action

    def _verify_keyframes(self, keyframe_set):

        if keyframe_set.Vertex.Count == 0:
            print("Shape motion has non-shape keyframes!")
            return False
        return True

    def _get_mesh_object(self, node_index: int):

        bone_name = self._bonemap[node_index]
        for child in self._bobject.children:
            if child.parent_bone == bone_name:
                break

        if child.parent_bone != bone_name:
            raise UserException(
                f"No mesh for keyframe {node_index} found! Did you"
                " perhaps merge the meshes of the armature?")

        if child.type != "MESH":
            raise UserException(
                f"The object (\"{child.name}\") for keyframe"
                f" {node_index} is not a mesh!")

        return child

    def process(
            self,
            motion,
            object: bpy.types.Object,
            min_frame_count: int = 0):

        super().process(motion, object)
        self._actions = {}

        if min_frame_count > 0:
            min_frame_count -= 1

        for node_keyframes in self._motion.Keyframes:
            for last in node_keyframes.Value.Vertex.Keys:
                pass
            if last > min_frame_count:
                min_frame_count = last

        if self._bobject.type != 'ARMATURE':
            self._convert(
                self._motion.Keyframes[0], self._bobject, min_frame_count)
        else:

            for node_keyframes in self._motion.Keyframes:

                if not self._verify_keyframes(node_keyframes.Value):
                    continue

                child = self._get_mesh_object(node_keyframes.Key)

                self._convert(node_keyframes.Value, child, min_frame_count)

        return self._actions


class CameraMotionProcessor:
    '''Used for importing Camera Motions'''

    _motion: any
    '''Source motion'''

    _keyframes: any
    '''Index 0 keyframes'''

    camera_setup: CameraSetup
    '''Camera setup to be used for FOV reference'''

    _action_set: CameraActionSet
    '''Resulting action set'''

    def __init__(self, camera_setup: CameraSetup):
        self.camera_setup = camera_setup
        self._motion = None
        self._keyframes = None
        self._action_set = None

    def _verify(self):
        '''Verifies that the motion can be properly imported'''

        if not self._motion.IsCameraMotion:
            raise UserException("Motion not a camera motion")

        keyframes = self._motion.Keyframes

        if keyframes.Count > 1 or not keyframes.ContainsKey(0):
            raise UserException("Motion not a valid camera motion (?)")

        self._keyframes = keyframes[0]

    def _create_actions(self):
        '''Creates the camera action set'''

        self._action_set = CameraActionSet.create_set(self._motion.Label)

    def _process_position(self):
        '''Processes the position keyframes'''

        TransformKeyframeProcessor(
            self._action_set.position,
            "Object Transforms"
        ).process_position_keyframes(
            self._keyframes.Position
        )

    def _process_target(self):
        '''Processes the target keyframes'''

        TransformKeyframeProcessor(
            self._action_set.target,
            "Object Transforms"
        ).process_position_keyframes(
            self._keyframes.Target
        )

    def _process_roll(self):
        '''Processes the roll keyframes'''

        roll = self._action_set.target.fcurves.new(
            "rotation_euler",
            index=2,
            action_group="Object Transforms").keyframe_points

        for kf_roll in self._keyframes.Roll:
            roll.insert(kf_roll.Key, -kf_roll.Value).interpolation = 'LINEAR'

    def _process_fov(self):
        '''Processes the Angle (Field of view) keyframes'''

        # we can only animate the focal length, not the angle,
        # so we need to calculate the focal length

        # angle = 2 * arctan(camera.sensor_width / (2 * focal length))
        # which means
        # focal length = 0.5 * (camera.sensor_width / tan(angle / 2))

        lens_size = self.camera_setup.camera_data.sensor_width

        fov = self._action_set.fov.fcurves.new(
            "lens", action_group="Camera").keyframe_points

        for kf_angle in self._keyframes.Angle:
            focal_length = 0.5 * (lens_size / math.tan(kf_angle.Value * 0.5))
            fov.insert(kf_angle.Key, focal_length).interpolation = 'LINEAR'

    def process(self, motion):
        '''Create actions off the input motion'''
        self._motion = motion
        self._verify()
        self._create_actions()

        self._process_position()
        self._process_target()
        self._process_roll()
        self._process_fov()

        return self._action_set

    @staticmethod
    def process_motion(
            motion: any,
            camera_setup: CameraSetup
    ) -> CameraActionSet:
        processor = CameraMotionProcessor(camera_setup)
        return processor.process(motion)
