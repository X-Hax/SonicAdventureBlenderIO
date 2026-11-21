from . import (
    import_operators, 
    texture_name_operators, 
    texture_operators,
    material_operators,
    info_operators
)

to_register = [
    import_operators.SAIO_OT_Import_Model,

    texture_operators.SAIO_OT_Textures_Add,
    texture_operators.SAIO_OT_Textures_Remove,
    texture_operators.SAIO_OT_Textures_Move,
    texture_operators.SAIO_OT_Textures_Clear,
    texture_operators.SAIO_OT_Textures_Autoname,
    texture_operators.SAIO_OT_Textures_Import_Archive,
    texture_operators.SAIO_OT_Textures_Import_Pack,
    texture_operators.SAIO_OT_Textures_Export_Archive,
    texture_operators.SAIO_OT_Textures_Export_Pack,

    texture_name_operators.SAIO_OT_TextureNames_Add,
    texture_name_operators.SAIO_OT_TextureNames_Remove,
    texture_name_operators.SAIO_OT_TextureNames_Move,
    texture_name_operators.SAIO_OT_TextureNames_Clear,
    texture_name_operators.SAIO_OT_TextureNames_Import,
    texture_name_operators.SAIO_OT_TextureNames_Export,

    material_operators.SAIO_OT_Material_UpdateProperties,
    material_operators.SAIO_OT_Material_UpdateActiveProperties,
    material_operators.SAIO_OT_Material_UpdateTextures,
    material_operators.SAIO_OT_Material_AttemptConvert,
    material_operators.SAIO_OT_Material_AssembleTextureList,

    info_operators.SAIO_OT_Info_Manual,
    info_operators.SAIO_OT_Info_Discord,
]