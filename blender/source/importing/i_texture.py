import bpy

from ..external import CTextureSet, CTexture, enums
from ..register.property_groups.texture_properties import SAIO_TextureList, SAIO_Texture


def import_texture_set(texture_list: SAIO_TextureList, texture_set: CTextureSet):
    texture_list.archive_format = enums.ARCHIVE_FORMAT[texture_set.archive_format]
    texture_list.compress = texture_set.compressed_archive

    for index in range(texture_set.textures_size):
        texture: CTexture = texture_set.textures[index]

        img = bpy.data.images.new(
            texture.name,
            texture.width,
            texture.height,
            alpha=True)

        pixel_size = texture.width * texture.height * 4
        factor = 1.0 / 256.0
        img.pixels = [texture.pixels[i] * factor for i in range(pixel_size)]
        img.update()
        img.use_fake_user = True
        img.pack()

        tex: SAIO_Texture = texture_list.new(name=texture.name, image=img)
        tex.global_index = texture.global_index
        tex.texture_type = enums.TEXTURE_TYPE[texture.texture_type]

        if texture_list.archive_format == 'PAK':
            tex.pak.image_format = enums.IMAGE_FORMAT[texture.image_format]

        elif texture_list.archive_format == 'GVM':
            tex.gv.format = enums.GV_FORMAT[texture.gv_format]
            tex.gv.has_mipmaps = texture.gv_has_mipmaps
            tex.gv.store_palette = texture.gv_store_palette
            tex.gv.palette_format = enums.GV_PALETTE_FORMAT[texture.gv_palette_format]

        elif texture_list.archive_format == 'PVM':
            tex.pv.data_format = enums.PV_TEXTURE_DATA_FORMAT[texture.pv_data_format]
            tex.pv.pixel_format = enums.PV_PIXEL_FORMAT[texture.pv_pixel_format]
            tex.pv.mipmap_mode = enums.PV_TEXTURE_DATA_FORMAT_MIPMAP[texture.pv_data_format]

        elif texture_list.archive_format == 'PVMX':
            tex.pvx.override_width = texture.override_width
            tex.pvx.override_height = texture.override_height
            tex.pak.image_format = enums.IMAGE_FORMAT[texture.image_format]



