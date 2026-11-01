# !!! GENERATED USING SAIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer

class CNode(ctypes.Structure):
    label: str
    parent_index: int
    transform: nettypes.CMatrix
    no_animate: bool
    no_morph: bool
    clip: bool
    cache_rotation: bool
    apply_cached_rotation: bool

CNode._fields_ = [
    ("label", ctypes.c_wchar_p),
    ("parent_index", ctypes.c_int),
    ("transform", nettypes.CMatrix),
    ("no_animate", ctypes.c_bool),
    ("no_morph", ctypes.c_bool),
    ("clip", ctypes.c_bool),
    ("cache_rotation", ctypes.c_bool),
    ("apply_cached_rotation", ctypes.c_bool),
]

