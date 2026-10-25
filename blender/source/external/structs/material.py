# !!! GENERATED USING SAIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer
from .ginja_tev_stage_parameter import CGinjaTevStageParameter
from .ginja_tex_gen_parameter import CGinjaTexGenParameter

class CMaterial(ctypes.Structure):
    diffuse: nettypes.CVector4
    specular: nettypes.CVector3
    specular_exponent: float
    ambient: nettypes.CVector4
    use_texture: bool
    texture_index: int
    clamp_u: bool
    clamp_v: bool
    mirror_u: bool
    mirror_v: bool
    normal_mapping: bool
    texcoord_precision_level: int
    texture_filter_mode: int
    anisotropic_filtering: bool
    mipmap_distance_multiplier: float
    alpha_mode: int
    source_blend_mode: int
    destination_blend_mode: int
    double_sided: bool
    ignore_lighting: bool
    ignore_ambient: bool
    ignore_specular: bool
    flat_shading: bool
    ginja_tev_stage_parameter: CGinjaTevStageParameter
    ginja_tex_gen_parameter: CGinjaTexGenParameter
    ginja_channel_count: int
    ginja_tex_gen_count: int
    ginja_tev_stage_count: int
    ginja_use_vertex_color_for_diffuse: bool
    ginja_use_vertex_color_for_ambient: bool
    ginja_texture_slot: int

CMaterial._fields_ = [
    ("diffuse", nettypes.CVector4),
    ("specular", nettypes.CVector3),
    ("specular_exponent", ctypes.c_float),
    ("ambient", nettypes.CVector4),
    ("use_texture", ctypes.c_bool),
    ("texture_index", ctypes.c_uint),
    ("clamp_u", ctypes.c_bool),
    ("clamp_v", ctypes.c_bool),
    ("mirror_u", ctypes.c_bool),
    ("mirror_v", ctypes.c_bool),
    ("normal_mapping", ctypes.c_bool),
    ("texcoord_precision_level", ctypes.c_ubyte),
    ("texture_filter_mode", ctypes.c_ubyte),
    ("anisotropic_filtering", ctypes.c_bool),
    ("mipmap_distance_multiplier", ctypes.c_float),
    ("alpha_mode", ctypes.c_ubyte),
    ("source_blend_mode", ctypes.c_ubyte),
    ("destination_blend_mode", ctypes.c_ubyte),
    ("double_sided", ctypes.c_bool),
    ("ignore_lighting", ctypes.c_bool),
    ("ignore_ambient", ctypes.c_bool),
    ("ignore_specular", ctypes.c_bool),
    ("flat_shading", ctypes.c_bool),
    ("ginja_tev_stage_parameter", CGinjaTevStageParameter),
    ("ginja_tex_gen_parameter", CGinjaTexGenParameter),
    ("ginja_channel_count", ctypes.c_ubyte),
    ("ginja_tex_gen_count", ctypes.c_ubyte),
    ("ginja_tev_stage_count", ctypes.c_ubyte),
    ("ginja_use_vertex_color_for_diffuse", ctypes.c_bool),
    ("ginja_use_vertex_color_for_ambient", ctypes.c_bool),
    ("ginja_texture_slot", ctypes.c_ubyte),
]

