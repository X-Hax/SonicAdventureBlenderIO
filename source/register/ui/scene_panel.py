import bpy
from .base_panel import PropertiesPanel
from ..property_groups.panel_properties import SAIO_PanelSettings
from ..property_groups.scene_properties import SAIO_Scene
from ...utility.draw import prop_advanced, expand_menu


class SAIO_PT_Scene(PropertiesPanel):
    bl_label = "SAIO Settings"
    bl_context = "scene"

    def draw_lighting_panel(
            layout: bpy.types.UILayout,
            setting_properties: SAIO_Scene,
            panel_settings: SAIO_PanelSettings):

        box = layout.box()
        if not expand_menu(
                box,
                panel_settings,
                "expanded_lighting_panel"):
            return

        def lighting_prop(label, name):
            prop_advanced(box, label, setting_properties, name)

        lighting_prop("Light Direction", "light_dir")
        lighting_prop("Light Color", "light_color")
        lighting_prop("Ambient Color", "light_ambient_color")

        box.separator()

        box.prop(setting_properties, "display_specular")
        lighting_prop("Viewport blend mode", "viewport_alpha_type")
        if setting_properties.viewport_alpha_type == 'CLIP':
            lighting_prop("Viewport blend cutoff", "viewport_alpha_cutoff")
        lighting_prop("Enable Backface Culling", "enable_backface_culling")

    def draw_scene_properties(
            layout: bpy.types.UILayout,
            scene: bpy.types.Scene,
            panel_settings: SAIO_PanelSettings):
        setting_properties: SAIO_Scene = scene.saio_scene

        layout.prop(setting_properties, "author")
        layout.prop(setting_properties, "description")
        layout.prop(setting_properties, "scene_type")
        layout.prop(setting_properties, "use_principled")

        SAIO_PT_Scene.draw_lighting_panel(
            layout,
            setting_properties,
            panel_settings
        )

    def draw_panel(self, context):
        SAIO_PT_Scene.draw_scene_properties(
            self.layout,
            context.scene,
            context.scene.saio_scene.panels)
