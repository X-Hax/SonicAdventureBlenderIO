# !!! GENERATED USING SAIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes, structs

FUNCTIONS = {
    "free_all": (
        None,
        None,
        "NO ERROR CHECK",
    ),
    "set_wchar_size": (
        (
            ctypes.c_int,
        ),
        None,
        "NO ERROR CHECK",
    ),
    "error_get": (
        None,
        ctypes.c_wchar_p,
        "NO ERROR CHECK",
    ),
    "matrix_multiply": (
        (
            nettypes.CMatrix,
            nettypes.CMatrix,
        ),
        nettypes.CMatrix,
    ),
    "matrix_invert": (
        (
            ctypes.POINTER(nettypes.CMatrix),
        ),
        ctypes.c_bool,
    ),
    "matrix_create_translation": (
        (
            nettypes.CVector3,
        ),
        nettypes.CMatrix,
    ),
    "matrix_create_rotation": (
        (
            nettypes.CVector3,
        ),
        nettypes.CMatrix,
    ),
    "matrix_create_from_quaternion": (
        (
            nettypes.CQuaternion,
        ),
        nettypes.CMatrix,
    ),
    "matrix_create_scale": (
        (
            nettypes.CVector3,
        ),
        nettypes.CMatrix,
    ),
    "matrix_decompose": (
        (
            nettypes.CMatrix,
            ctypes.POINTER(nettypes.CVector3),
            ctypes.POINTER(nettypes.CQuaternion),
            ctypes.POINTER(nettypes.CVector3),
        ),
        None,
    ),
    "matrix_to_euler": (
        (
            nettypes.CMatrix,
        ),
        nettypes.CVector3,
    ),
    "quaternion_create_from_rotation_matrix": (
        (
            nettypes.CMatrix,
        ),
        nettypes.CQuaternion,
    ),
}
