from ..register.property_groups.texture_properties import SAIO_TextureList
from ..register.property_groups.texturename_properties import SAIO_TextureNameList
from ..dotnet import System, SA3D_Common, SA3D_Texturing, SA3D_Archival, SAIO_NET
from ..exceptions import SAIOException


def create_texnames_from_names(
        texture_names: SAIO_TextureNameList,
        name: str):

    texname_list = []
    for texture_name in texture_names:
        texname = texture_name.name if texture_name.name != '!NULL' else None
        texname_list.append(SA3D_Texturing.TEXTURE_NAME(texname.lower(), 0, 0))

    tex_array = SA3D_Common.LABELED_ARRAY[SA3D_Texturing.TEXTURE_NAME](
        name + "_names", texname_list)
    return SA3D_Texturing.TEXTURE_NAME_LIST(name, tex_array)


def create_texnames_from_textures(
        textures: SAIO_TextureList,
        name: str):

    texname_list = []
    for texture in textures:
        texname_list.append(SA3D_Texturing.TEXTURE_NAME(
            texture.name.lower().ljust(28), 0, 0))

    tex_array = SA3D_Common.LABELED_ARRAY[SA3D_Texturing.TEXTURE_NAME](
        name + "_names", texname_list)
    return SA3D_Texturing.TEXTURE_NAME_LIST(name, tex_array)


def create_texture_set(texture_list: SAIO_TextureList):
    sa3d_textures = []
    for texture in texture_list:

        is_index4 = None
        if texture.texture_type == "ID4":
            is_index4 = True
        elif texture.texture_type == "ID8":
            is_index4 = False

        if texture.image is None or not texture.image.has_data:
            sa3d_texture = SAIO_NET.TEXTURE.Create(
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
            sa3d_texture = SAIO_NET.TEXTURE.Create(
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

    return SA3D_Texturing.TEXTURE_SET(sa3d_textures)

def encode_texture_archive(
        texture_set,
        filepath: str,
        archive_type: str):

    from os import path

    archive = None
    if archive_type == "PAK":
        normpath = path.normpath(filepath)
        directory = path.dirname(normpath)
        file_name = path.splitext(path.basename(normpath))[0]

        if path.sep != "\\":
            # PAK requires windows seperators
            directory.replace(path.sep, "\\")

        if "\\gd_pc\\" in directory:
            pak_path = (
                "..\\..\\..\\sonic2\\resource"
                + directory[directory.index("\\gd_pc\\"):])
        else:
            pak_path = "..\\..\\..\\sonic2\\resource\\gd_pc\\prs\\"

        archive = SA3D_Archival.PAK_ARCHIVE.FromTextureSet(
            texture_set, file_name, pak_path)

    elif archive_type == "PVMX":
        archive = SA3D_Archival.PVMX.PVMXFromTextureSet(texture_set)

    elif archive_type == "PVM":
        archive = SA3D_Archival.PVM.FromTextureSet(texture_set)

    elif archive_type == "GVM":
        archive = SA3D_Archival.GVM.FromTextureSet(texture_set)

    else:
        raise SAIOException(f"Invalid Archive type \"{archive_type}\"")

    return archive

def save_texture_archive(
        texture_set,
        filepath: str,
        archive_type: str,
        compress: bool):

    archive = encode_texture_archive(texture_set, filepath, archive_type)

    file_data = archive.WriteArchiveToBytes()
    if compress:
        file_data = SA3D_Archival.PRS.CompressPRS(file_data)

    System.FILE.WriteAllBytes(filepath, file_data)
