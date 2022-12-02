from ..register.property_groups.texture_properties import (
    SAIO_TextureList
)

from ..register.property_groups.texturename_properties import (
    SAIO_TextureNameList
)


def create_texnames_from_names(
        texture_names: SAIO_TextureNameList,
        name: str):

    from SA3D.Texturing.NJS import NjsTexList, NjsTexName

    list = []
    for texture_name in texture_names:
        texname = texture_name.name if texture_name.name != '!NULL' else None
        list.append(NjsTexName(texname.lower(), 0, 0))

    return NjsTexList(name, name + "_names", list)


def create_texnames_from_textures(
        textures: SAIO_TextureList,
        name: str):

    from SA3D.Texturing.NJS import NjsTexList, NjsTexName
    list = []
    for texture in textures:
        list.append(NjsTexName(texture.name.lower().ljust(28), 0, 0))

    return NjsTexList(name, name + "_names", list)


def create_texture_set(texture_list: SAIO_TextureList):
    from SA3D.Modeling.Blender import Texture
    from SA3D.Texturing import TextureSet

    sa3d_textures = []
    for texture in texture_list:

        is_index4 = None
        if texture.texture_type == "ID4":
            is_index4 = True
        elif texture.texture_type == "ID8":
            is_index4 = False

        if texture.image is None or not texture.image.has_data:
            sa3d_texture = Texture.Create(
                texture.name.lower(),
                texture.global_index,
                2,
                2,
                is_index4,
                [255, 255, 255, 255,
                 255, 255, 255, 255,
                 255, 255, 255, 255,
                 255, 255, 255, 255]
            )
        else:
            sa3d_texture = Texture.Create(
                texture.name.lower(),
                texture.global_index,
                texture.image.size[0],
                texture.image.size[1],
                is_index4,
                texture.image.pixels
            )

        sa3d_texture.OverrideWidth = texture.override_width
        sa3d_texture.OverrideHeight = texture.override_height

        sa3d_textures.append(sa3d_texture)

    return TextureSet(sa3d_textures)


def save_texture_archive(
        texture_set,
        filepath: str,
        archive_type: str,
        compress: bool):

    from os import path

    archive = None
    if archive_type == "PAK":
        normpath = path.normpath(filepath)
        directory = path.dirname(normpath)
        file_name = path.splitext(path.basename(normpath))[0]

        if "\\gd_pc\\" in directory:
            pak_path = (
                "..\\..\\..\\sonic2\\resource"
                + directory[directory.index("\\gd_pc\\"):])
        else:
            pak_path = "..\\..\\..\\sonic2\\resource\\gd_pc\\prs\\"

        from SA3D.Archival.PAK import PAKArchive
        archive = PAKArchive.FromTextureSet(
            texture_set, file_name, pak_path)

    elif archive_type == "PVMX":
        from SA3D.Archival.Tex.PVMX import PVMXArchive
        archive = PVMXArchive.PVMXFromTextureSet(texture_set)

    elif archive_type == "PVM":
        from SA3D.Archival.Tex.PV import PVM
        archive = PVM.FromTextureSet(texture_set)

    elif archive_type == "GVM":
        from SA3D.Archival.Tex.GV import GVM
        archive = GVM.FromTextureSet(texture_set)

    else:
        raise Exception(f"Invalid Archive type \"{archive_type}\"")

    file_data = archive.Write()
    if compress:
        from SA3D.Archival import PRS
        file_data = PRS.CompressPRS(file_data)

    from System.IO import File
    File.WriteAllBytes(filepath, file_data)
