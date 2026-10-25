# !!! GENERATED USING SAIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer

class CMeshConverterParameters(ctypes.Structure):
    split_weighted: bool
    use_meta_weights: bool
    high_precision_weights: bool
    merge_vertices: bool
    vertex_merge_distance: float

CMeshConverterParameters._fields_ = [
    ("split_weighted", ctypes.c_bool),
    ("use_meta_weights", ctypes.c_bool),
    ("high_precision_weights", ctypes.c_bool),
    ("merge_vertices", ctypes.c_bool),
    ("vertex_merge_distance", ctypes.c_float),
]

