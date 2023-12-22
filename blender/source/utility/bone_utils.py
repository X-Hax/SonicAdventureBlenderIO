import bpy
from mathutils import Vector, Matrix
from ..exceptions import UserException


def _get_bone(
        bone: bpy.types.PoseBone,
        force_sort: bool,
        shape: bool,
        result: list[str]):
    if (not bone.bone.saio_node.no_animate and not shape
            or not bone.bone.saio_node.no_morph and shape):
        result.append(bone.name)

    children = list(bone.children)
    if force_sort:
        children.sort(key=lambda b: b.name.lower())
    for b in children:
        _get_bone(b, force_sort, shape, result)


def get_bone_map(
        armature_object: bpy.types.Object,
        force_sort: bool,
        shape: bool) -> list[str]:
    parentless_bones = [
        b for b in armature_object.pose.bones
        if b.parent is None]

    if len(parentless_bones) > 1:
        raise UserException("Armature invalid! More than one root bone!")

    bone_nodes = []
    _get_bone(parentless_bones[0], force_sort, shape, bone_nodes)

    return bone_nodes


def get_bone_transforms(bone: bpy.types.PoseBone) -> tuple[Vector, Matrix]:
    local_matrix: Matrix = bone.bone.matrix_local

    if bone.parent is not None:
        parent_matrix: Matrix = bone.parent.bone.matrix_local.inverted()
        local_matrix = parent_matrix @ local_matrix

    position_offset, local_rotation, _ = local_matrix.decompose()
    rotation_matrix = local_rotation.to_matrix().to_4x4()

    return position_offset, rotation_matrix
