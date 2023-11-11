from . import (
    land_entry_panel,
    event_entry_panel,
    material_mass_edit_panel,
    material_panel,
    node_panel,
    mesh_panel,
    scene_panel,
    landtable_panel,
    texture_panel,
    event_node_uv_anim_panel,
    event_uv_anim_panel,
    event_panel,
    menus,
    texturename_panel,

    viewport_object,
    viewport_scene,
    viewport_toolbar
)

to_register = [
    material_panel.SAIO_PT_Material,
    land_entry_panel.SAIO_PT_LandEntry,
    event_entry_panel.SAIO_PT_EventEntry,
    node_panel.SAIO_PT_Node,
    node_panel.SAIO_PT_Node_Bone,
    mesh_panel.SAIO_PT_Mesh,
    landtable_panel.SAIO_PT_Landtable,

    texture_panel.SAIO_UL_TextureList,
    texture_panel.SAIO_MT_TextureContextMenu,
    texturename_panel.SAIO_UL_TextureNameList,
    texturename_panel.SAIO_MT_TextureNameContextMenu,

    texture_panel.SAIO_PT_ObjectTextures,
    texture_panel.SAIO_PT_SceneTextures,
    texturename_panel.SAIO_PT_SceneTexturenames,
    texturename_panel.SAIO_PT_ObjectTexturenames,

    event_node_uv_anim_panel.SAIO_UL_EventNodeUVAnimList,
    event_node_uv_anim_panel.SAIO_MT_EventNodeUVAnimContextMenu,
    event_node_uv_anim_panel.SAIO_PT_EventNodeUVAnimPanel,

    event_uv_anim_panel.SAIO_UL_EventUVAnimList,
    event_uv_anim_panel.SAIO_MT_EventUVAnimContextMenu,

    event_panel.SAIO_UL_EventSceneList,
    event_panel.SAIO_MT_EventSceneContextMenu,
    event_panel.SAIO_PT_Event,

    scene_panel.SAIO_PT_Scene,

    viewport_toolbar.SAIO_PT_VTP_Import,
    viewport_toolbar.SAIO_PT_VTP_Export,
    viewport_toolbar.SAIO_PT_VTP_Material,
    viewport_toolbar.SAIO_PT_VTP_Utilities,
    material_mass_edit_panel.SAIO_PT_MaterialMassEdit,
    viewport_toolbar.SAIO_PT_VTP_Migration,
    viewport_toolbar.SAIO_PT_VTP_Info,

    viewport_scene.SAIO_PT_VSP_Settings,
    viewport_scene.SAIO_PT_VSP_Textures,
    viewport_scene.SAIO_PT_VSP_Texturenames,
    viewport_scene.SAIO_PT_VSP_LandTable,
    viewport_scene.SAIO_PT_VSP_Event,

    viewport_object.SAIO_PT_VOP_LandEntry,
    viewport_object.SAIO_PT_VOP_EventEntry,
    viewport_object.SAIO_PT_VOP_EventNodeUVAnim,
    viewport_object.SAIO_PT_VOP_Node,
    viewport_object.SAIO_PT_VOP_Textures,
    viewport_object.SAIO_PT_VOP_Texturenames,
    viewport_object.SAIO_PT_VPMesh,
    viewport_object.SAIO_PT_VPMaterial,

    menus.TOPBAR_MT_SAIO_Export,
    menus.TOPBAR_MT_SAIO_Import
]


def register():
    pass


def unregister():
    menus.TOPBAR_MT_SAIO_Export.unregister()
    menus.TOPBAR_MT_SAIO_Import.unregister()
