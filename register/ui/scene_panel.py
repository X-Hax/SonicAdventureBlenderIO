import bpy

from ..property_groups import (
    SAIO_PanelSettings,
    SAIO_Scene
)

from .draw import (
    prop_advanced,
    expand_menu
)

from ..operators import texture_operators as texop


TEXTURELIST_TOOLS = [
    (
        texop.SAIO_OT_Textures_Add.bl_idname,
        "ADD",
        {}
    ),
    (
        texop.SAIO_OT_Textures_Remove.bl_idname,
        "REMOVE",
        {}
    ),
    None,
    (
        texop.SAIO_OT_Textures_Move.bl_idname,
        "TRIA_UP",
        {"direction": "UP"}
    ),
    (
        texop.SAIO_OT_Textures_Move.bl_idname,
        "TRIA_DOWN",
        {"direction": "DOWN"}
    )
]


class SAIO_UL_TextureList(bpy.types.UIList):

    def draw_item(
            self,
            context: bpy.types.Context,
            layout: bpy.types.UILayout,
            data,
            item,
            icon: str,
            active_data,
            active_propname,
            index,
            flt_flag):

        split = layout.split(factor=0.6)

        split.prop(
            item,
            "name",
            text="",
            emboss=False,
            icon_value=icon,
            icon='X' if item.image is None else 'CHECKMARK')

        split.prop(
            item,
            "global_id",
            text=str(index),
            emboss=False,
            icon_value=icon)


class SAIO_MT_TextureContextMenu(bpy.types.Menu):
    bl_label = "Texture list specials"

    def draw(self, context):
        layout = self.layout

        layout.operator(texop.SAIO_OT_Textures_Autoname.bl_idname)
        layout.operator(texop.SAIO_OT_Textures_Clear.bl_idname)
        layout.separator()
        layout.operator(texop.SAIO_OT_Textures_Import.bl_idname)


class SAIO_PT_Scene(bpy.types.Panel):
    bl_label = "SAIO Scene"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_texture_list(
            layout: bpy.types.UILayout,
            setting_properties: SAIO_Scene,
            panel_settings: SAIO_PanelSettings):

        box = layout.box()
        if not expand_menu(
                box,
                panel_settings,
                "expanded_texture_panel"):
            return

        box.prop(setting_properties, "correct_material_textures")

        row = box.row()
        row.template_list(
            "SAIO_UL_TextureList",
            "",
            setting_properties,
            "texture_list",
            setting_properties,
            "active_texture_index")

        column = row.column()

        for tool in TEXTURELIST_TOOLS:
            if tool is None:
                column.separator()
                continue

            operator = column.operator(
                tool[0],
                icon=tool[1],
                text="")

            for k, v in tool[2].items():
                setattr(operator, k, v)

        column.menu(
            "SAIO_MT_TextureContextMenu",
            icon='DOWNARROW_HLT',
            text="")

        if setting_properties.active_texture_index >= 0:
            texture = setting_properties.texture_list[
                setting_properties.active_texture_index]
            box.prop_search(texture, "image", bpy.data, "images")

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

    def draw_panel(
            layout: bpy.types.UILayout,
            scene: bpy.types.Scene,
            panel_settings: SAIO_PanelSettings):
        setting_properties: SAIO_Scene = scene.saio_scene

        layout.prop(setting_properties, "author")
        layout.prop(setting_properties, "description")
        layout.prop(setting_properties, "scene_is_level")
        layout.prop(setting_properties, "use_principled")

        SAIO_PT_Scene.draw_texture_list(
            layout,
            setting_properties,
            panel_settings
        )

        SAIO_PT_Scene.draw_lighting_panel(
            layout,
            setting_properties,
            panel_settings
        )

    def draw(self, context):
        SAIO_PT_Scene.draw_panel(
            self.layout,
            context.scene,
            context.scene.saio_scene.panels)
