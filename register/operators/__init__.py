import bpy

from .export_model_operators import (
    SAIO_OT_Export_SA1MDL,
    SAIO_OT_Export_SA2MDL,
    SAIO_OT_Export_SA2BMDL,
    SAIO_OT_Export_SA1LVL,
    SAIO_OT_Export_SA2LVL,
    SAIO_OT_Export_SA2BLVL,
)

from .import_operators import (
    SAIO_OT_Import_Level,
    SAIO_OT_Import_Model
)

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

from .material_operators import (
    SAIO_OT_Material_TextureFromID,
    SAIO_OT_Material_TextureToID,
    SAIO_OT_Material_UpdateNodes,
    SAIO_OT_Material_UpdateActiveNodes
)

to_register = [
    SAIO_OT_Export_SA1MDL,
    SAIO_OT_Export_SA2MDL,
    SAIO_OT_Export_SA2BMDL,
    SAIO_OT_Export_SA1LVL,
    SAIO_OT_Export_SA2LVL,
    SAIO_OT_Export_SA2BLVL,

    SAIO_OT_Import_Level,
    SAIO_OT_Import_Model,

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
    SAIO_OT_Material_UpdateActiveNodes
]
