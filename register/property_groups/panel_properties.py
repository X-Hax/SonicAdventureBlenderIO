import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty
)


class SAIO_PanelSettings(bpy.types.PropertyGroup):
    """ Property Group for managing expanded Material Properties menus"""

    # === Quick Edit ===

    expanded_material_quick_edit: BoolProperty(
        name="Material Quick Edit",
        description=(
            "A menu for quickly assigning material"
            " properties to mutliple objects"
        ),
        default=False
    )

    expanded_node_quick_edit: BoolProperty(
        name="Node Quick Edit",
        description=(
            "A menu for quickly assigning Node"
             " properties to mutliple objects"
        ),
        default=False
    )

    expanded_land_entry_quick_edit: BoolProperty(
        name="Land Entry Quick Edit",
        description=(
            "A menu for quickly assigning Land Entry"
             " properties to mutliple objects"
        ),
        default=False
    )

    expanded_mesh_quick_edit: BoolProperty(
        name="Mesh Quick Edit",
        description=(
            "A menu for quickly assigning mesh"
            " properties to mutliple objects"
        ),
        default=False
    )

    # === Material ===

    expanded_texture_properties: BoolProperty(
        name="Texture properties",
        default=False
    )

    expanded_rendering_properties: BoolProperty(
        name="Rendering properties",
        default=False
    )

    expanded_gc_properties: BoolProperty(
        name="SA2B specific",
        default=False
    )

    expanded_gc_texgen: BoolProperty(
        name="Generate texture coords",
        default=False
    )

    # === Land Entry ===

    expanded_surface_attributes: BoolProperty(
        name="Surface Attributes",
        default=False
    )

    land_entry_surface_attributes_editmode: EnumProperty(
        name="Surface attributes edit mode",
        description="How to edit the surface flags",
        items=(
             ("UNIVERSAL", "Universal",
                 "edit all surface attributes simultaneously"),
            ("SA1", "Adventure 1",
                 "Edit surface attributes specific to sa1"),
            ("SA2", "Adventure 2",
                 "Edit surface attributes specific to sa2"),
        ),
        default="UNIVERSAL"
    )

    # === Settings ===

    expanded_landtable_panel: BoolProperty(
        name="Landtable Info",
        default=False
    )

    expanded_texture_panel: BoolProperty(
        name="Texture List Info",
        default=False
    )

    expanded_lighting_panel: BoolProperty(
        name="Lighting Data",
        default=False
    )

    @classmethod
    def register(cls):
        pass
