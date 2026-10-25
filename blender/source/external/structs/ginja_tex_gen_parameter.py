# !!! GENERATED USING SAIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer

class CGinjaTexGenParameter(ctypes.Structure):
    tex_coord: int
    tex_gen_type: int
    tex_gen_source: int
    matrix_id: int

CGinjaTexGenParameter._fields_ = [
    ("tex_coord", ctypes.c_ubyte),
    ("tex_gen_type", ctypes.c_ubyte),
    ("tex_gen_source", ctypes.c_ubyte),
    ("matrix_id", ctypes.c_ubyte),
]

