# !!! GENERATED USING SAIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer
from .node import CNode
from .mesh_conversion_info import CMeshConversionInfo

class CModel(ctypes.Structure):
    name: str
    description: str
    author: str
    rotation_mode: int
    nodes: TPointer['CNode']
    nodes_size: int
    meshes: TPointer['CMeshConversionInfo']
    meshes_size: int

CModel._fields_ = [
    ("name", ctypes.c_wchar_p),
    ("description", ctypes.c_wchar_p),
    ("author", ctypes.c_wchar_p),
    ("rotation_mode", ctypes.c_int),
    ("nodes", ctypes.POINTER(CNode)),
    ("nodes_size", ctypes.c_int),
    ("meshes", ctypes.POINTER(CMeshConversionInfo)),
    ("meshes_size", ctypes.c_int),
]

