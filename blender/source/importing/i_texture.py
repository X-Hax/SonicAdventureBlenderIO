import bpy
from ..dotnet import SA3D_Texturing, SAIO_NET

def process_texture_set(texture_set, texture_list):
    for texture in texture_set.Textures:
        img = bpy.data.images.new(
            texture.Name,
            texture.Width,
            texture.Height,
            alpha=True)

        img.pixels = SAIO_NET.TEXTURE.GetData(texture)
        img.update()
        img.use_fake_user = True
        img.pack()

        tex = texture_list.new(name=texture.Name, image=img)
        tex.global_index = texture.GlobalIndex
        tex.override_width = texture.OverrideWidth
        tex.override_height = texture.OverrideHeight

        if isinstance(tex, SA3D_Texturing.INDEX_TEXTURE):
            tex.texture_type = "ID4" if tex.IsIndex4 else "ID8"
        else:
            tex.texture_type = "RGBA"


def process_texture_names(texture_names, texname_list):
    texname_list.clear()
    for njs_texname in texture_names.TextureNames:
        if njs_texname.Name is None:
            texname_list.new(name="!NULL")
        else:
            texname_list.new(name=njs_texname.Name)
