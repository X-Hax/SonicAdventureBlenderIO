from ..operators import *

IMPORT = "/ui/toolbar/tools/import/"
EXPORT = "/ui/toolbar/tools/export/"
MATERIAL = "/ui/toolbar/tools/material/"
UTILITIES = "/ui/toolbar/tools/utilities/"
MME = "/ui/toolbar/tools/material_mass_edit/"
MIGRATION = "/ui/toolbar/tools/migration/"

TEXTURES = "/ui/textures/"
TEXNAMES = "/ui/texturenames/"

raw_mapping = [
    (import_operators.SAIO_OT_Import_Model, f"{IMPORT}#import-model"),
    (import_operators.SAIO_OT_Import_Landtable, f"{IMPORT}#import-landtable"),
    (import_operators.SAIO_OT_Import_Event, f"{IMPORT}#import-sa2-event"),
    (path_operators.SAIO_OT_Import_Path, f"{IMPORT}#import-path-ini"),
    (anim_import_operators.SAIO_OT_Import_Node_Animation, f"{IMPORT}#import-node-animation"),
    (anim_import_operators.SAIO_OT_Import_Shape_Animation, f"{IMPORT}#import-shape-animation"),
    (anim_import_operators.SAIO_OT_Import_Camera_Animation, f"{IMPORT}#import-camera-animation"),

    (export_operators.SAIO_OT_Export_SA1MDL, f"{EXPORT}#export-mdl"),
    (export_operators.SAIO_OT_Export_SA2MDL, f"{EXPORT}#export-mdl"),
    (export_operators.SAIO_OT_Export_SA2BMDL, f"{EXPORT}#export-mdl"),
    (export_operators.SAIO_OT_Export_SA1LVL, f"{EXPORT}#export-lvl"),
    (export_operators.SAIO_OT_Export_SA2LVL, f"{EXPORT}#export-lvl"),
    (export_operators.SAIO_OT_Export_SA2BLVL, f"{EXPORT}#export-lvl"),
    (path_operators.SAIO_OT_Export_Path, f"{EXPORT}#export-path"),
    (anim_export_operators.SAIO_OT_Export_Node_Animation, f"{EXPORT}#export-node-animation"),
    (anim_export_operators.SAIO_OT_Export_Node_Animations, f"{EXPORT}#batch-export-node-animations"),
    (anim_export_operators.SAIO_OT_Export_Shape_Animation, f"{EXPORT}#export-shape-animation"),
    (anim_export_operators.SAIO_OT_Export_Camera_Animation, f"{EXPORT}#export-camera-animation"),

    (material_operators.SAIO_OT_Material_AssembleTextureList, f"{MATERIAL}#attempt-convert-materials"),
    (material_operators.SAIO_OT_Material_AttemptConvert, f"{MATERIAL}#assemble-texture-list"),
    (material_operators.SAIO_OT_Material_UpdateActiveProperties, f"{MATERIAL}#update-material-properties"),
    (material_operators.SAIO_OT_Material_UpdateProperties, f"{MATERIAL}#update-material-properties"),
    (material_operators.SAIO_OT_Material_UpdateTextures, f"{MATERIAL}#update-material-textures"),

    (tool_operators.SAIO_OT_TestBakeAnimation, f"{UTILITIES}#bake-node-animation"),
    (tool_operators.SAIO_OT_ArmatureFromObjects, f"{UTILITIES}#armature-from-objects"),
    (tool_operators.SAIO_OT_ArmaturCorrectVisual, f"{UTILITIES}#correct-armature-visuals"),
    (tool_operators.SAIO_OT_SetupCamera, f"{UTILITIES}#create-camera-setup"),
    (tool_operators.SAIO_OT_CopyVertexIndicesToClipboard, f"{UTILITIES}#copy-vertex-indices-to-clipboard"),
    (tool_operators.SAIO_OT_AutoNodeAttributes, f"{UTILITIES}#auto-node-attributes"),
    (path_operators.SAIO_OT_Path_Generate, f"{UTILITIES}#generate-path"),

    (material_mass_edit_operators.SAIO_OT_MaterialMassEdit_Set, MME),
    (material_mass_edit_operators.SAIO_OT_MaterialMassEdit_Reset, f"{MME}#reset-parameters"),

    (migration_operators.SAIO_OT_MigrateCheck, f"{MIGRATION}#check-for-migrate-data"),
    (migration_operators.SAIO_OT_MigrateArmature, f"{MIGRATION}#migrate-armature"),
    (migration_operators.SAIO_OT_MigrateData, f"{MIGRATION}#migrate-data"),
    (migration_operators.SAIO_OT_MigratePath, f"{MIGRATION}#migrate-path"),

    (texture_operators.SAIO_OT_Textures_Autoname, f"{TEXTURES}#autoname-entries"),
    (texture_operators.SAIO_OT_Textures_Clear, f"{TEXTURES}#clear-list"),
    (texture_operators.SAIO_OT_Textures_Import_Archive, f"{TEXTURES}#import-texture-archive"),
    (texture_operators.SAIO_OT_Textures_Import_Pack, f"{TEXTURES}#import-texture-pack"),
    (texture_operators.SAIO_OT_Textures_Export_Archive, f"{TEXTURES}#export-as-texture-archive"),
    (texture_operators.SAIO_OT_Textures_Export_Pack, f"{TEXTURES}#export-as-texture-pack"),
    (texture_operators.SAIO_OT_Texture_ToAssetLibrary, f"{TEXTURES}#generate-material-asset-library"),

    (texture_name_operators.SAIO_OT_TextureNames_Clear, f"{TEXNAMES}#clear-list"),
    (texture_name_operators.SAIO_OT_TextureNames_Import, f"{TEXNAMES}#import-texture-list"),
    (texture_name_operators.SAIO_OT_TextureNames_Export, f"{TEXNAMES}#export-texture-list"),
]

manual_mapping = []
for raw in raw_mapping:
    manual_mapping.append(("bpy.ops." + raw[0].bl_idname + "*", raw[1]))
