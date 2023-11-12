import bpy
from mathutils import Matrix, Vector, Euler


def parse_net_to_bpy_matrix(matrix):
    '''Casts a .NET matrix directly to a Blender matrix'''
    return Matrix((
        (matrix.M11, matrix.M21, matrix.M31, matrix.M41),
        (matrix.M12, matrix.M22, matrix.M32, matrix.M42),
        (matrix.M13, matrix.M23, matrix.M33, matrix.M43),
        (matrix.M14, matrix.M24, matrix.M34, matrix.M44)
    ))


def net_to_bpy_matrix(matrix):
    '''Converts a .NET matrix to a Blender matrix'''

    # in the current fake module version (3.4), the decompose function is incorrectly declared
    position, rotation, scale = parse_net_to_bpy_matrix(matrix).decompose()  # pylint: disable=assignment-from-no-return

    new_pos = Vector((position.x, -position.z, position.y))
    new_scale = Vector((scale.x, scale.z, scale.y))

    euler_rotation: Euler = rotation.to_euler('XZY')
    new_euler_rotation = Euler(
        (euler_rotation.x, -euler_rotation.z, euler_rotation.y))

    # It is not declared incorrectly here, but still throws the same error. Weird.
    new_rotation = new_euler_rotation.to_quaternion() # pylint: disable=assignment-from-no-return

    return Matrix.LocRotScale(new_pos, new_rotation, new_scale)


def net_to_bpy_matrices(matrices):
    '''Converts a list of .NET matrices to Blender matrices'''
    return [net_to_bpy_matrix(matrix) for matrix in matrices]


def get_bone_transforms(bone: bpy.types.PoseBone):
    local_matrix = bone.bone.matrix_local

    if bone.parent is not None:
        parent_matrix = bone.parent.bone.matrix_local.inverted()
        local_matrix = parent_matrix @ local_matrix

    position_offset, local_rotation, _ = local_matrix.decompose()
    rotation_matrix = local_rotation.to_matrix().to_4x4()

    return position_offset, rotation_matrix
