# !!! GENERATED USING SAIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer
from .texture import CTexture

class CTextureSet(ctypes.Structure):
    textures: TPointer['CTexture']
    textures_size: int
    archive_format: int
    compressed_archive: bool

CTextureSet._fields_ = [
    ("textures", ctypes.POINTER(CTexture)),
    ("textures_size", ctypes.c_int),
    ("archive_format", ctypes.c_int),
    ("compressed_archive", ctypes.c_bool),
]

