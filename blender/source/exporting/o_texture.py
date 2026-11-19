import bpy
import ctypes

from ..external import CTextureSet, CTexture, enums, util
from ..register.property_groups.texture_properties import SAIO_TextureList, SAIO_Texture
from ..exceptions import SAIOUserException

def create_texture_set(texture_list: SAIO_TextureList, force_archive_format: str | None = None):
    c_textures = []

    archive_format = force_archive_format
    if archive_format is None:
        archive_format = texture_list.archive_format

    for i, tex in enumerate(texture_list):
        tex: SAIO_Texture = tex

        if tex.image is None:
            raise SAIOUserException(f"Texture list slot {i} (\"{tex.slot_name}\") has no image!")

        c_texture = CTexture()
        c_texture.name = tex.slot_name
        c_texture.texture_type = enums.TEXTURE_TYPE.index(tex.texture_type)
        c_texture.global_index = tex.global_index
        c_texture.dither = tex.dither

        image: bpy.types.Image = tex.image
        c_texture.width = image.size[0]
        c_texture.height = image.size[1]
        c_texture.pixels = util.as_array([int(max(0, min(1, f)) * 255) for f in image.pixels], ctypes.c_ubyte)
        if texture_list.archive_format == 'PAK':
            c_texture.image_format = enums.IMAGE_FORMAT.index(tex.pak.image_format)
            c_texture.image_has_mipmaps = tex.pak.has_mipmaps
            c_texture.pak_punchthrough = tex.pak.punchthrough

        elif texture_list.archive_format == 'GVM':
            c_texture.gv_format = enums.GV_FORMAT.index(tex.gv.format)
            c_texture.gv_has_mipmaps = tex.gv.has_mipmaps
            c_texture.gv_store_palette = tex.gv.store_palette
            c_texture.gv_palette_format = enums.GV_PALETTE_FORMAT.index(tex.gv.palette_format)

        elif texture_list.archive_format == 'PVM':
            c_texture.pv_data_format = enums.PV_TEXTURE_DATA_FORMAT.index(tex.pv.data_format)
            c_texture.pv_pixel_format = enums.PV_PIXEL_FORMAT.index(tex.pv.pixel_format)
            c_texture.pv_data_format = enums.PV_TEXTURE_DATA_FORMAT_MIPMAP.index(tex.pv.mipmap_mode)

        elif texture_list.archive_format == 'PVMX':
            c_texture.override_width = tex.pvx.override_width
            c_texture.override_height = tex.pvx.override_height
            c_texture.image_format = enums.IMAGE_FORMAT.index(tex.pak.image_format)
            c_texture.image_has_mipmaps = tex.pak.has_mipmaps

        c_textures.append(c_texture)

    result =  CTextureSet(
        textures = util.as_array(c_textures, CTexture),
        textures_size = len(c_textures),
        archive_format = enums.ARCHIVE_FORMAT.index(archive_format),
        compressed_archive = texture_list.compress
    )

    return ctypes.pointer(result)