# !!! GENERATED USING SAIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer

class CVertex(ctypes.Structure):
    position: nettypes.CVector3
    normal: nettypes.CVector3
    user_attributes: int
    weights: TPointer['float']

CVertex._fields_ = [
    ("position", nettypes.CVector3),
    ("normal", nettypes.CVector3),
    ("user_attributes", ctypes.c_uint),
    ("weights", ctypes.POINTER(ctypes.c_float)),
]

