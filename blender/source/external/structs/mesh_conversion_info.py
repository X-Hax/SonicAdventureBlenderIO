# !!! GENERATED USING SAIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer
from .mesh import CMesh

class CMeshConversionInfo(ctypes.Structure):
    mesh: CMesh
    attached_node_index: int
    has_normals: bool
    has_diffuse_colors: bool
    has_specular_colors: bool
    volume_mesh: bool
    chunk_vertex_type: int
    no_bounds: bool

CMeshConversionInfo._fields_ = [
    ("mesh", CMesh),
    ("attached_node_index", ctypes.c_int),
    ("has_normals", ctypes.c_bool),
    ("has_diffuse_colors", ctypes.c_bool),
    ("has_specular_colors", ctypes.c_bool),
    ("volume_mesh", ctypes.c_bool),
    ("chunk_vertex_type", ctypes.c_ubyte),
    ("no_bounds", ctypes.c_bool),
]

