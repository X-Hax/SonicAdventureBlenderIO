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

CCorner._fields_ = [
    ("vertex_index", ctypes.c_ushort),
    ("diffuse", nettypes.CVector4),
    ("specular", nettypes.CVector4),
    ("tex_coord", nettypes.CVector2),
]

