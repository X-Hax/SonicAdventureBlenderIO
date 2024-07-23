import bpy
from .base_panel import PropertiesPanel
from ..property_groups.scene_properties import SAIO_Scene
from ...utility.draw import prop_advanced


class SAIO_PT_Scene(PropertiesPanel):
    bl_label = "SAIO Settings"
    bl_context = "scene"

    @staticmethod
    def draw_lighting_panel(
            layout: bpy.types.UILayout,
            setting_properties: SAIO_Scene):

        header, panel = layout.panel("saio_scene_lighting", default_closed=True)
        header.label(text="Lighting Data")
        if not panel:
            return

        def lighting_prop(label, name):
            prop_advanced(panel, label, setting_properties, name)

        lighting_prop("Light Direction", "light_dir")
        lighting_prop("Light Color", "light_color")
        lighting_prop("Ambient Color", "light_ambient_color")

        panel.separator()

        panel.prop(setting_properties, "display_specular")
        lighting_prop("Enable Backface Culling", "enable_backface_culling")

    @staticmethod
    def draw_scene_properties(
            layout: bpy.types.UILayout,
            scene: bpy.types.Scene):
        setting_properties: SAIO_Scene = scene.saio_scene

        layout.prop(setting_properties, "author")
        layout.prop(setting_properties, "description")
        layout.prop(setting_properties, "scene_type")
        layout.prop(setting_properties, "use_principled")

        SAIO_PT_Scene.draw_lighting_panel(
            layout,
            setting_properties
        )

    def draw_panel(self, context):
        SAIO_PT_Scene.draw_scene_properties(
            self.layout,
            context.scene)
