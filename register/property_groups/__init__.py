"""All property groups declared by the addon"""

from . import (
    land_entry,
    material,
    mesh,
    node,
    panel_properties,
    project,
    landtable,
    quick_edit,
    settings,
    texture
)

# Order is important
to_register = [
    panel_properties.SAIO_PanelSettings,
    land_entry.SAIO_LandEntry,
    material.SAIO_Material,
    mesh.SAIO_Mesh,
    node.SAIO_Node,
    project.SAIO_Project,
    texture.SAIO_Texture,
    landtable.SAIO_LandTable,

    quick_edit.SAIO_QuickEdit,
    settings.SAIO_Settings
]
