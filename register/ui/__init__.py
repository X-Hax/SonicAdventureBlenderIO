from . import (
    land_entry_panel,
    material_panel,
    node_panel,
    mesh_panel,
    scene_panel,
    landtable_panel,
    viewport_toolbar,
    quick_edit_panel,
    menus
)

to_register = [
    material_panel.SAIO_PT_Material,
    land_entry_panel.SAIO_PT_LandEntry,
    node_panel.SAIO_PT_Node,
    node_panel.SAIO_PT_Node_Bone,
    mesh_panel.SAIO_PT_Mesh,
    landtable_panel.SAIO_PT_Landtable,

    scene_panel.SAIO_UL_TextureList,
    scene_panel.SAIO_MT_TextureContextMenu,
    scene_panel.SAIO_PT_Scene,

    viewport_toolbar.SAIO_PT_VPTools,
    viewport_toolbar.SAIO_PT_VPSettings,
    viewport_toolbar.SAIO_PT_VPLandTable,
    viewport_toolbar.SAIO_PT_VPLandEntry,
    viewport_toolbar.SAIO_PT_VPNode,
    viewport_toolbar.SAIO_PT_VPMesh,
    viewport_toolbar.SAIO_PT_VPMaterial,

    quick_edit_panel.SAIO_PT_QuickEdit,

    menus.TOPBAR_MT_SAIO_Export,
    menus.TOPBAR_MT_SAIO_Import
]


def register():
    pass


def unregister():
    menus.TOPBAR_MT_SAIO_Export.unregister()
    menus.TOPBAR_MT_SAIO_Import.unregister()
