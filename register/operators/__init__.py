from . import (
    texture_operators,
    quick_edit_operators
)

to_register = [
    texture_operators.SAIO_OT_Textures_Add,
    texture_operators.SAIO_OT_Textures_Remove,
    texture_operators.SAIO_OT_Textures_Move,
    texture_operators.SAIO_OT_Textures_Autoname,
    texture_operators.SAIO_OT_Textures_Clear,
    texture_operators.SAIO_OT_Textures_Import,

    quick_edit_operators.SAIO_OT_QuickEdit_Set,
    quick_edit_operators.SAIO_OT_QuickEdit_Select,
]
