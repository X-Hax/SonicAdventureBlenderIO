# !!! GENERATED USING SAIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer

class CArray(ctypes.Structure):
    array: ctypes.c_void_p
    size: int

CArray._fields_ = [
    ("array", ctypes.c_void_p),
    ("size", ctypes.c_int),
]

