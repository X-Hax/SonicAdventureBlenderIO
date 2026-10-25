# !!! GENERATED USING SAIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer

class CGinjaTevStageParameter(ctypes.Structure):
    tev_stage: int
    tex_coord: int
    tex_map: int
    color_channel: int

CGinjaTevStageParameter._fields_ = [
    ("tev_stage", ctypes.c_ubyte),
    ("tex_coord", ctypes.c_ubyte),
    ("tex_map", ctypes.c_ubyte),
    ("color_channel", ctypes.c_ubyte),
]

