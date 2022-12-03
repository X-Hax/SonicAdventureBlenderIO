import bpy

from ..property_groups import (
    landtable_properties
)

from .draw import (
    prop_advanced
)


class SAIO_PT_Landtable(bpy.types.Panel):
    bl_label = "SAIO Landtable"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_panel(
            layout: bpy.types.UILayout,
            landtable_properties: landtable_properties.SAIO_LandTable):

        prop_advanced(
            layout,
            "Name: ",
            landtable_properties,
            "name"
        )

        prop_advanced(
            layout,
            "Draw Distance:",
            landtable_properties,
            "draw_distance"
        )

        layout.prop(landtable_properties, "double_sided_collision")

        layout.separator(factor=2)

        prop_advanced(
            layout,
            "Texture filename:",
            landtable_properties,
            "tex_file_name"
        )

        prop_advanced(
            layout,
            "Texlist Pointer (hex):  0x",
            landtable_properties,
            "tex_list_pointer"
        )

    def draw(self, context):

        if not context.scene.saio_settings.scene_is_level:
            self.layout.box().label(text="Scene is not marked as a level")
            return

        SAIO_PT_Landtable.draw_panel(
            self.layout,
            context.scene.saio_settings.landtable
        )
