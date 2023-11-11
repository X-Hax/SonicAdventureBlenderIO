"""All property groups declared by the addon"""

from . import (
    material_mass_edit_properties,
    panel_properties,
    land_entry_properties,
    material_properties,
    mesh_properties,
    node_properties,
    event_entry_properties,
    texture_properties,
    texturename_properties,
    landtable_properties,
    event_uv_anim_properties,
    event_node_uv_anim_properties,
    event_properties,
    scene_properties,
    addon_preferences,
)

# Order is important
to_register = [
    panel_properties.SAIO_PanelSettings,
    land_entry_properties.SAIO_LandEntry,
    material_properties.SAIO_Material,
    mesh_properties.SAIO_Mesh,
    node_properties.SAIO_Node,
    event_entry_properties.SAIO_EventEntry,
    texture_properties.SAIO_Texture,
    texture_properties.SAIO_TextureList,
    texturename_properties.SAIO_TextureName,
    texturename_properties.SAIO_TextureNameList,
    landtable_properties.SAIO_LandTable,

    event_uv_anim_properties.SAIO_Event_UVAnim,
    event_uv_anim_properties.SAIO_Event_UVAnimList,
    event_node_uv_anim_properties.SAIO_EventNode_UVAnim,
    event_node_uv_anim_properties.SAIO_EventNode_UVAnimList,
    event_properties.SAIO_EventScene,
    event_properties.SAIO_OverrideUpgrade,
    event_properties.SAIO_AttachUpgrade,
    event_properties.SAIO_Event,

    material_mass_edit_properties.SAIO_MaterialMassEdit,
    scene_properties.SAIO_Scene,

    addon_preferences.SAIO_AddonPreferences
]
