from mathutils import Matrix, Vector
from ..external import SAIONET, CMatrix, CVector3, CQuaternion

def c_to_bpy_matrix(matrix: CMatrix):
    return Matrix((
        (matrix.m11, -matrix.m31, matrix.m21, matrix.m41),
        (-matrix.m13, matrix.m33, -matrix.m23, -matrix.m43),
        (matrix.m12, -matrix.m32, matrix.m22, matrix.m42),
        (0, 0, 0, 1),
    ))

def c_to_bpy_bone_xz_matrix(matrix: CMatrix):
    return Matrix((
        (matrix.m31, matrix.m11, matrix.m21, matrix.m41),
        (-matrix.m33, -matrix.m13, -matrix.m23, -matrix.m43),
        (matrix.m32, matrix.m12, matrix.m22, matrix.m42),
        (0, 0, 0, 1),
    ))

def c_transforms_to_bpy_matrix(position: CVector3, euler_rotation: CVector3, scale: CVector3):

    position_mtx = SAIONET.matrix_create_translation(position)
    rotation_matrix = SAIONET.matrix_create_rotation(euler_rotation)
    scale_mtx = SAIONET.matrix_create_scale(scale)

    matrix = SAIONET.matrix_multiply(SAIONET.matrix_multiply(scale_mtx, rotation_matrix), position_mtx)
    return c_to_bpy_matrix(matrix)


def c_to_bpy_vector(vector):
    return Vector((vector.x, -vector.z, vector.y))


def c_to_bpy_scale(scale):
    return Vector((scale.x, scale.z, scale.y))


def c_to_bpy_quaternion(quat: CQuaternion):
    return c_to_bpy_matrix(SAIONET.matrix_create_from_quaternion(quat)).to_quaternion()