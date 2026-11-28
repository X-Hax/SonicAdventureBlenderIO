# !!! GENERATED USING SAIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer
from .node import CNode

class CLevelModel(ctypes.Structure):
    node: CNode
    mesh_index: int
    blockbit: int
    surface_attributes: int

CLevelModel._fields_ = [
    ("node", CNode),
    ("mesh_index", ctypes.c_int),
    ("blockbit", ctypes.c_int),
    ("surface_attributes", ctypes.c_int),
]

