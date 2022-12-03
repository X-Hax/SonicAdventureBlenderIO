"""All property groups declared by the addon"""

from . import (
    land_entry_properties,
    landtable_properties,
    material_properties,
    mesh_properties,
    node_properties,
    panel_properties,
    project_properties,
    quick_edit_properties,
    scene_properties,
    texture_properties
)

# Order is important
to_register = [
    panel_properties.SAIO_PanelSettings,
    land_entry_properties.SAIO_LandEntry,
    material_properties.SAIO_Material,
    mesh_properties.SAIO_Mesh,
    node_properties.SAIO_Node,
    project_properties.SAIO_Project,
    texture_properties.SAIO_Texture,
    landtable_properties.SAIO_LandTable,

    quick_edit_properties.SAIO_QuickEdit,
    scene_properties.SAIO_Settings
]
