from . import (
    export_operators,
    anim_export_operators,
    import_operators,
    anim_import_operators,
    material_mass_edit_operators,
    texture_operators,
    texture_name_operators,
    event_operators,
    event_node_uv_anim_operators,
    event_uv_anim_operators,
    material_operators,
    tool_operators,
    path_operators,
    migration_operators,
    info_operators
)

to_register = [
    export_operators.SAIO_OT_Export_SA1MDL,
    export_operators.SAIO_OT_Export_SA2MDL,
    export_operators.SAIO_OT_Export_SA2BMDL,
    export_operators.SAIO_OT_Export_SA1LVL,
    export_operators.SAIO_OT_Export_SA2LVL,
    export_operators.SAIO_OT_Export_SA2BLVL,
    export_operators.SAIO_OT_Export_Event,

    anim_export_operators.SAIO_OT_Export_Node_Animation,
    anim_export_operators.SAIO_OT_Export_Node_Animations,
    anim_export_operators.SAIO_OT_Export_Camera_Animation,
    anim_export_operators.SAIO_OT_Export_Shape_Animation,

    import_operators.SAIO_OT_Import_Landtable,
    import_operators.SAIO_OT_Import_Model,
    import_operators.SAIO_OT_Import_Event,

    anim_import_operators.SAIO_OT_Import_Node_Animation,
    anim_import_operators.SAIO_OT_Import_Camera_Animation,
    anim_import_operators.SAIO_OT_Import_Shape_Animation,

    texture_operators.SAIO_OT_Textures_Add,
    texture_operators.SAIO_OT_Textures_Remove,
    texture_operators.SAIO_OT_Textures_Move,
    texture_operators.SAIO_OT_Textures_Autoname,
    texture_operators.SAIO_OT_Textures_Clear,

    texture_operators.SAIO_OT_Textures_Import_Pack,
    texture_operators.SAIO_OT_Textures_Import_Archive,
    texture_operators.SAIO_OT_Textures_Export_Archive,
    texture_operators.SAIO_OT_Textures_Export_Pack,
    texture_operators.SAIO_OT_Texture_ToAssetLibrary,

    texture_name_operators.SAIO_OT_TextureNames_Add,
    texture_name_operators.SAIO_OT_TextureNames_Remove,
    texture_name_operators.SAIO_OT_TextureNames_Move,
    texture_name_operators.SAIO_OT_TextureNames_Clear,
    texture_name_operators.SAIO_OT_TextureNames_Import,
    texture_name_operators.SAIO_OT_TextureNames_Export,

    event_operators.SAIO_OT_EventScene_Add,
    event_operators.SAIO_OT_EventScene_Remove,
    event_operators.SAIO_OT_EventScene_Move,
    event_operators.SAIO_OT_EventScene_Clear,

    event_node_uv_anim_operators.SAIO_OT_EventNode_UVAnim_Add,
    event_node_uv_anim_operators.SAIO_OT_EventNode_UVAnim_Remove,
    event_node_uv_anim_operators.SAIO_OT_EventNode_UVAnim_Move,
    event_node_uv_anim_operators.SAIO_OT_EventNode_UVAnim_Clear,

    event_uv_anim_operators.SAIO_OT_Event_UVAnim_Add,
    event_uv_anim_operators.SAIO_OT_Event_UVAnim_Remove,
    event_uv_anim_operators.SAIO_OT_Event_UVAnim_Move,
    event_uv_anim_operators.SAIO_OT_Event_UVAnim_Clear,

    material_mass_edit_operators.SAIO_OT_MaterialMassEdit_Set,
    material_mass_edit_operators.SAIO_OT_MaterialMassEdit_Reset,

    material_operators.SAIO_OT_Material_UpdateProperties,
    material_operators.SAIO_OT_Material_UpdateActiveProperties,
    material_operators.SAIO_OT_Material_UpdateTextures,
    material_operators.SAIO_OT_Material_AttemptConvert,
    material_operators.SAIO_OT_Material_AssembleTextureList,

    tool_operators.SAIO_OT_TestBakeAnimation,
    tool_operators.SAIO_OT_ArmatureFromObjects,
    tool_operators.SAIO_OT_ArmaturCorrectVisual,
    tool_operators.SAIO_OT_SetupCamera,
    tool_operators.SAIO_OT_CopyVertexIndicesToClipboard,
    tool_operators.SAIO_OT_AutoNodeAttributes,

    path_operators.SAIO_OT_Import_Path,
    path_operators.SAIO_OT_Path_Generate,
    path_operators.SAIO_OT_Export_Path,

    migration_operators.SAIO_OT_MigrateCheck,
    migration_operators.SAIO_OT_MigrateData,
    migration_operators.SAIO_OT_MigrateArmature,
    migration_operators.SAIO_OT_MigratePath,

    info_operators.SAIO_OT_Info_Manual,
    info_operators.SAIO_OT_Info_Discord,
]
