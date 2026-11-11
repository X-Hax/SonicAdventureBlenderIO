# !!! GENERATED USING SAIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer

class CTexture(ctypes.Structure):
    name: str
    width: int
    height: int
    texture_type: int
    pixels: TPointer['int']
    global_index: int
    dither: bool
    gv_format: int
    gv_has_mipmaps: bool
    gv_store_palette: bool
    gv_palette_format: int
    pv_data_format: int
    pv_pixel_format: int
    override_width: int
    override_height: int
    image_format: int

CTexture._fields_ = [
    ("name", ctypes.c_wchar_p),
    ("width", ctypes.c_int),
    ("height", ctypes.c_int),
    ("texture_type", ctypes.c_int),
    ("pixels", ctypes.POINTER(ctypes.c_ubyte)),
    ("global_index", ctypes.c_int),
    ("dither", ctypes.c_bool),
    ("gv_format", ctypes.c_int),
    ("gv_has_mipmaps", ctypes.c_bool),
    ("gv_store_palette", ctypes.c_bool),
    ("gv_palette_format", ctypes.c_int),
    ("pv_data_format", ctypes.c_int),
    ("pv_pixel_format", ctypes.c_int),
    ("override_width", ctypes.c_int),
    ("override_height", ctypes.c_int),
    ("image_format", ctypes.c_int),
]

