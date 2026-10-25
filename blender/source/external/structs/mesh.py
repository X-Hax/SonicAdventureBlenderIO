# !!! GENERATED USING SAIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer
from .vertex import CVertex
from .corner import CCorner
from .material import CMaterial

class CMesh(ctypes.Structure):
    label: str
    weight_node_index_map: TPointer['int']
    weight_node_index_map_size: int
    vertices: TPointer['CVertex']
    vertices_size: int
    triangle_sets: TPointer[TPointer['CCorner']]
    materials: TPointer['CMaterial']
    triangle_set_sizes: TPointer['int']
    triangle_sets_size: int

CMesh._fields_ = [
    ("label", ctypes.c_wchar_p),
    ("weight_node_index_map", ctypes.POINTER(ctypes.c_int)),
    ("weight_node_index_map_size", ctypes.c_int),
    ("vertices", ctypes.POINTER(CVertex)),
    ("vertices_size", ctypes.c_int),
    ("triangle_sets", ctypes.POINTER(ctypes.POINTER(CCorner))),
    ("materials", ctypes.POINTER(CMaterial)),
    ("triangle_set_sizes", ctypes.POINTER(ctypes.c_int)),
    ("triangle_sets_size", ctypes.c_int),
]

