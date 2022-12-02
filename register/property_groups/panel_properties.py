import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty
)


class SAIO_PanelSettings(bpy.types.PropertyGroup):
    """ Property Group for managing expanded Material Properties menus"""

    # === Quick Edit ===

    expanded_quick_edit_panel: BoolProperty(
        name="Quick Edit",
        default=False
    )

    expanded_material_edit: BoolProperty(
        name="Material Quick Edit",
        description=(
            "A menu for quickly assigning material"
            " properties to mutliple objects"
        ),
        default=False
    )

    expanded_land_entry_edit: BoolProperty(
        name="LandEntry Quick Edit",
        description=(
            "A menu for quickly assigning LandEntry"
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

    # === Object ===

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

    expanded_object_attributes: BoolProperty(
        name="Object Attributes",
        default=False
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
