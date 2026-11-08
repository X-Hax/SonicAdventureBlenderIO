from . import import_operators, texture_name_operators

to_register = [
    texture_name_operators.SAIO_OT_TextureNames_Add,
    texture_name_operators.SAIO_OT_TextureNames_Remove,
    texture_name_operators.SAIO_OT_TextureNames_Move,
    texture_name_operators.SAIO_OT_TextureNames_Clear,
    texture_name_operators.SAIO_OT_TextureNames_Import,
    texture_name_operators.SAIO_OT_TextureNames_Export,

    import_operators.SAIO_OT_Import_Model
]