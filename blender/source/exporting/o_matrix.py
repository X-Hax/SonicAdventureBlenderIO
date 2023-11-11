from mathutils import Matrix, Vector, Euler


def parse_bpy_to_net_matrix(matrix: Matrix):
    from System.Numerics import Matrix4x4
    return Matrix4x4(
        matrix[0][0], matrix[1][0], matrix[2][0], matrix[3][0],
        matrix[0][1], matrix[1][1], matrix[2][1], matrix[3][1],
        matrix[0][2], matrix[1][2], matrix[2][2], matrix[3][2],
        matrix[0][3], matrix[1][3], matrix[2][3], matrix[3][3],
    )


def bpy_to_net_matrix(matrix: Matrix):
    '''Converts a blender matrix to an SAIO matrix'''
    position, rotation, scale = matrix.decompose()

    new_pos = Vector((position.x, position.z, -position.y))
    new_scale = Vector((scale.x, scale.z, scale.y))

    euler_rotation: Euler = rotation.to_euler('XYZ')
    new_euler_rotation = Euler(
        (euler_rotation.x, euler_rotation.z, -euler_rotation.y), 'XZY')
    new_rotation = new_euler_rotation.to_quaternion()

    return parse_bpy_to_net_matrix(
        Matrix.LocRotScale(new_pos, new_rotation, new_scale))

