# !!! GENERATED USING SAIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer
from .level_model import CLevelModel
from .mesh_conversion_info import CMeshConversionInfo

class CLevel(ctypes.Structure):
    name: str
    description: str
    author: str
    format: int
    rotation_mode: int
    models: TPointer['CLevelModel']
    models_size: int
    visual_count: int
    meshes: TPointer['CMeshConversionInfo']
    meshes_size: int
    level_attributes: int
    draw_distance: float
    texture_file_name: str
    texture_list_address: int

CLevel._fields_ = [
    ("name", ctypes.c_wchar_p),
    ("description", ctypes.c_wchar_p),
    ("author", ctypes.c_wchar_p),
    ("format", ctypes.c_int),
    ("rotation_mode", ctypes.c_int),
    ("models", ctypes.POINTER(CLevelModel)),
    ("models_size", ctypes.c_int),
    ("visual_count", ctypes.c_int),
    ("meshes", ctypes.POINTER(CMeshConversionInfo)),
    ("meshes_size", ctypes.c_int),
    ("level_attributes", ctypes.c_int),
    ("draw_distance", ctypes.c_float),
    ("texture_file_name", ctypes.c_wchar_p),
    ("texture_list_address", ctypes.c_int),
]

