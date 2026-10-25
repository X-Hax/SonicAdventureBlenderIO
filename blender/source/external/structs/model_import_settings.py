# !!! GENERATED USING SAIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer
from .mesh_converter_parameters import CMeshConverterParameters

class CModelImportSettings(ctypes.Structure):
    use_quaternions: bool
    mesh_converter_parameters: CMeshConverterParameters

CModelImportSettings._fields_ = [
    ("use_quaternions", ctypes.c_bool),
    ("mesh_converter_parameters", CMeshConverterParameters),
]

