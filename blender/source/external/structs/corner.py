# !!! GENERATED USING SAIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer

class CCorner(ctypes.Structure):
    vertex_index: int
    diffuse: nettypes.CVector4
    specular: nettypes.CVector4
    tex_coord: nettypes.CVector2
    attributes1: int
    attributes2: int
    attributes3: int

CCorner._fields_ = [
    ("vertex_index", ctypes.c_ushort),
    ("diffuse", nettypes.CVector4),
    ("specular", nettypes.CVector4),
    ("tex_coord", nettypes.CVector2),
    ("attributes1", ctypes.c_ushort),
    ("attributes2", ctypes.c_ushort),
    ("attributes3", ctypes.c_ushort),
]

