import bpy

from .base_panel import PropertiesPanel

from ..property_groups.scene_properties import SAIO_Scene
from ..property_groups.landtable_properties import SAIO_LandTable

from ...utility.draw import prop_advanced


class SAIO_PT_Landtable(PropertiesPanel):
    bl_label = "SAIO Landtable"
    bl_context = "scene"

    @staticmethod
    def draw_landtable_properties(
            layout: bpy.types.UILayout,
            landtable_properties: SAIO_LandTable):

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

    # === overriden methods === #

    @classmethod
    def verify(cls, context: bpy.types.Context):
        return SAIO_Scene.check_is_landtable(context)

    def draw_panel(self, context):

        SAIO_PT_Landtable.draw_landtable_properties(
            self.layout,
            context.scene.saio_scene.landtable)
