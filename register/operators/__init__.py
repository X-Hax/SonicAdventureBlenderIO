from .texture_operators import (
    SAIO_OT_Textures_Add,
    SAIO_OT_Textures_Remove,
    SAIO_OT_Textures_Move,
    SAIO_OT_Textures_Autoname,
    SAIO_OT_Textures_Clear,
    SAIO_OT_Textures_Import,
)

from .quick_edit_operators import (
    SAIO_OT_QuickEdit_Set,
    SAIO_OT_QuickEdit_Select
)

from .material_tools import (
    SAIO_OT_Material_TextureFromID,
    SAIO_OT_Material_TextureToID,
    SAIO_OT_Material_UpdateNodes
)

to_register = [
    SAIO_OT_Textures_Add,
    SAIO_OT_Textures_Remove,
    SAIO_OT_Textures_Move,
    SAIO_OT_Textures_Autoname,
    SAIO_OT_Textures_Clear,
    SAIO_OT_Textures_Import,

    SAIO_OT_QuickEdit_Set,
    SAIO_OT_QuickEdit_Select,

    SAIO_OT_Material_TextureFromID,
    SAIO_OT_Material_TextureToID,
    SAIO_OT_Material_UpdateNodes,
]
