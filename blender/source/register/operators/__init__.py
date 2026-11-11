from . import import_operators, texture_name_operators, texture_operators

to_register = [
    texture_operators.SAIO_OT_Textures_Add,
    texture_operators.SAIO_OT_Textures_Remove,
    texture_operators.SAIO_OT_Textures_Move,
    texture_operators.SAIO_OT_Textures_Clear,
    texture_operators.SAIO_OT_Textures_Autoname,
    texture_operators.SAIO_OT_Textures_Import_Archive,

    texture_name_operators.SAIO_OT_TextureNames_Add,
    texture_name_operators.SAIO_OT_TextureNames_Remove,
    texture_name_operators.SAIO_OT_TextureNames_Move,
    texture_name_operators.SAIO_OT_TextureNames_Clear,
    texture_name_operators.SAIO_OT_TextureNames_Import,
    texture_name_operators.SAIO_OT_TextureNames_Export,

    import_operators.SAIO_OT_Import_Model
]