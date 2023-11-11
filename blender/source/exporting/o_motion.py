import math

import bpy
from bpy.types import Object as BObject
from mathutils import Vector, Matrix

from . import o_keyframes
from ..utility import dll_utils, camera_utils, bone_utils
from ..utility.anim_parameters import AnimParameters


def get_action(
        id_data: bpy.types.ID,
        frame: int,
        ignore_selected: bool = False):

    animation_data: bpy.types.AnimData = id_data.animation_data
    if animation_data is None:
        return None

    if animation_data.action is not None and not ignore_selected:
        return animation_data.action

    if len(animation_data.nla_tracks) == 0:
        return None

    track: bpy.types.NlaTrack = None
    if animation_data.nla_tracks.active is not None:
        track = animation_data.nla_tracks.active
    else:
        for nla_track in animation_data.nla_tracks:
            if nla_track.is_solo:
                track = nla_track
                break
        if track is None:
            track = animation_data.nla_tracks[0]

    if not ignore_selected:

        # check if one is active
        for strip in track.strips:
            if strip.type == 'CLIP' and strip.active:
                return strip.action

        # check if one is selected
        for strip in track.strips:
            if strip.type == 'CLIP' and strip.select:
                return strip.action

    # get the one on display right now
    for strip in track.strips:
        if (strip.type == 'CLIP'
                and strip.frame_start <= frame
                and strip.frame_end > frame):
            return strip.action

    return None


def get_frame_range(actions: list[bpy.types.Action]):
    start = None
    end = None
    for action in actions:
        if action is None:
            continue

        ac_start = math.ceil(action.frame_range[0])
        ac_end = math.floor(action.frame_range[1])

        if start is None:
            start = ac_start
            end = ac_end
        else:
            start = max(start, ac_start)
            end = min(end, ac_end)

    return start, end


def convert_to_node_motion(
        object: BObject,
        force_sort_bones: bool,
        fcurves: bpy.types.ActionFCurves,
        frame_range: tuple[float, float],
        name: str,
        anim_parameters: AnimParameters):

    dll_utils.load_library()

    start = math.ceil(frame_range[0])
    end = math.floor(frame_range[1])
    frame_number = end - start + 1

    evaluator = o_keyframes.KeyframeEvaluator(
        start, end, anim_parameters)

    from SA3D.Modeling.ObjectData.Animation import Motion

    if object.type == "ARMATURE":

        bone_nodes = bone_utils.get_bone_map(object, force_sort_bones, False)
        motion = Motion(frame_number, len(bone_nodes))

        for index, bone_name in enumerate(bone_nodes):
            if index == 0 and not anim_parameters.bone_localspace:
                base_matrix = object.matrix_world.copy()
            else:
                base_matrix = Matrix.Identity(4)

            bone = object.pose.bones[bone_name]
            bone_data_prefix = f"pose.bones[\"{bone_name}\"]."

            position_offset, rotation_matrix \
                = bone_utils.get_bone_transforms(bone)

            keyframes = evaluator.evaluate_node_keyframe_set(
                fcurves,
                bone_data_prefix,
                base_matrix,
                bone.rotation_mode,
                bone.bone.saio_node.rotate_zyx,
                position_offset,
                rotation_matrix
            )

            if keyframes is not None:
                motion.Keyframes.Add(index, keyframes)

    else:
        motion = Motion(frame_number, 1)

        keyframes = evaluator.evaluate_node_keyframe_set(
            fcurves,
            "",
            Matrix.Identity(4),
            object.rotation_mode,
            object.saio_node.rotate_zyx,
            Vector(),
            Matrix.Identity(4)
        )

        motion.Keyframes.Add(0, keyframes)

    motion.Label = name
    motion.ShortRot = anim_parameters.short_rot

    return motion


def convert_to_camera_motion(
        camera_setup: camera_utils.CameraSetup,
        camera_actions: camera_utils.CameraActionSet,
        name: str,
        anim_parameters: AnimParameters):

    dll_utils.load_library()

    start, end = get_frame_range(camera_actions.as_list())
    frame_number = end - start + 1

    evaluator = o_keyframes.KeyframeEvaluator(
        start, end, anim_parameters)

    from SA3D.Modeling.ObjectData.Animation import Motion
    motion = Motion(frame_number, 1)

    keyframes = evaluator.evaluate_camera_keyframe_set(
        camera_setup, camera_actions)

    if keyframes is None:
        return None

    motion.Keyframes.Add(0, keyframes)
    motion.Label = name

    return motion
