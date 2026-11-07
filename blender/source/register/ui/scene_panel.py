import bpy
from .base_panel import PropertiesPanel
from ..property_groups.scene_properties import SAIO_Scene
from ...utility.draw import col_prop


class SAIO_PT_Scene(PropertiesPanel):
    bl_label = "SAIO Settings"
    bl_context = "scene"


    @staticmethod
    def draw_scene_properties(
            layout: bpy.types.UILayout,
            scene: bpy.types.Scene):
        setting_properties: SAIO_Scene = scene.saio_scene

        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(setting_properties, "author")
        layout.prop(setting_properties, "description")

        split = layout.split(factor=0.4)
        split.alignment = 'RIGHT'
        split.label(text="Scene format")
        row = split.row()
        row.prop(setting_properties, "file_format", text="")
        row.prop(setting_properties, "scene_type", text="")

        if setting_properties.file_format == 'CHUNK' and setting_properties.scene_type == 'MDL':
            col_prop(layout, setting_properties, "chao_chunk")

    def draw_panel(self, context):
        SAIO_PT_Scene.draw_scene_properties(
            self.layout,
            context.scene
        )
