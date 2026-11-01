# !!! GENERATED USING SAIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer
from .mesh_converter_parameters import CMeshConverterParameters

class CModelExportSettings(ctypes.Structure):
    rotation_mode: int
    mesh_converter_parameters: CMeshConverterParameters

CModelExportSettings._fields_ = [
    ("rotation_mode", ctypes.c_int),
    ("mesh_converter_parameters", CMeshConverterParameters),
]

