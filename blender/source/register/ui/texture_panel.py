import bpy

from .base_panel import PropertiesPanel
from ..property_groups.texture_properties import SAIO_Texture, PV_MIPMAP_FORMATS
from ..operators import texture_operators as texop

from ...utility.draw import draw_list, col_prop, TOOL_PROPERTY


TEXTURELIST_TOOLS: list[TOOL_PROPERTY] = [
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
            active_property,
            index,
            flt_flag):

        split = layout.split(factor=0.4)

        split.label(
            text=str(index),
            icon='X' if item.image is None else 'CHECKMARK')

        split.prop(
            item,
            "name",
            text="",
            emboss=False)

class BaseTextureContextMenu(bpy.types.Menu):
    bl_label = "Texture list operations"

    def draw(self, context):
        layout = self.layout

        def mode_op(bl_idname: str):
            op = layout.operator(bl_idname)
            op.mode = self.texture_mode

        mode_op(texop.SAIO_OT_Textures_Autoname.bl_idname)
        mode_op(texop.SAIO_OT_Textures_Clear.bl_idname)
        layout.separator()
        mode_op(texop.SAIO_OT_Textures_Import_Archive.bl_idname)

class SAIO_MT_TextureContextMenuScene(BaseTextureContextMenu):
    texture_mode = 'SCENE'

class SAIO_MT_TextureContextMenuObject(BaseTextureContextMenu):
    texture_mode = 'OBJECT'


def _draw_texture_properties(
    layout: bpy.types.UILayout,
    archive_format: str,
    texture_properties: SAIO_Texture):

    layout.prop_search(texture_properties, "image", bpy.data, "images")
    layout.prop(texture_properties, "name")
    layout.prop(texture_properties, "texture_type")
    layout.prop(texture_properties, "global_index")

    layout.separator(type="LINE")

    def draw_dither(format:str):
        column = layout.column()
        column.active = format in { 'INDEX4', 'INDEX8' } and texture_properties.texture_type == 'COLOR'
        col_prop(column, texture_properties, "dither")

    if archive_format == 'PAK':
        layout.prop(texture_properties.pak, "image_format")

    elif archive_format == 'GVM':
        layout.prop(texture_properties.gv, "format")
        col_prop(layout, texture_properties.gv, "has_mipmaps")

        palette_layout = layout.column()
        palette_layout.active = texture_properties.gv.format in { 'INDEX8', 'INDEX4' } and texture_properties.texture_type == 'COLOR'
        col_prop(palette_layout, texture_properties.gv, "store_palette")
        palette_layout.prop(texture_properties.gv, "palette_format")

        draw_dither(texture_properties.gv.format)

    elif archive_format == 'PVM':
        layout.prop(texture_properties.pv, "data_format")
        layout.prop(texture_properties.pv, "pixel_format")

        if texture_properties.pv.data_format == 'SQUARETWIDDLED':  
            layout.prop(texture_properties.pv, "mipmap_mode")
        elif texture_properties.pv.data_format in PV_MIPMAP_FORMATS:
            col_prop(layout, texture_properties.pv, "has_mipmaps")

        draw_dither(texture_properties.pv.data_format)

    elif archive_format == 'PVMX':
        layout.prop(texture_properties.pvx, "override_width")
        layout.prop(texture_properties.pvx, "override_height")
        layout.prop(texture_properties.pak, "image_format")


def draw_texture_list_panel(
        layout: bpy.types.UILayout,
        world_container: any,
        world_prop_name: str,
        is_object: bool):

    layout.use_property_split = True
    layout.use_property_decorate = False

    layout.template_ID(world_container, world_prop_name, new="world.new")
    world = getattr(world_container, world_prop_name)

    if world is None:
        return

    texture_list = world.saio_texture_list

    layout.prop(texture_list, "archive_format")

    if texture_list.archive_format in { 'PVM', 'GVM' }:
        layout.prop(texture_list, "palette_handling")
        

    col_prop(layout, texture_list, "compress")

    def set_op(operator, i):
        if is_object:
            operator.mode = "OBJECT"

    draw_list(
        layout,
        SAIO_UL_TextureList,
        SAIO_MT_TextureContextMenuObject if is_object else SAIO_MT_TextureContextMenuScene,
        texture_list,
        TEXTURELIST_TOOLS,
        set_op
    )

    if texture_list.active_index >= 0:
        _draw_texture_properties(
            layout,
            texture_list.archive_format,
            texture_list[texture_list.active_index]
        )


class SAIO_PT_SceneTextures(PropertiesPanel):
    bl_context = "scene"
    bl_label = "SAIO Scene Textures"

    def draw_panel(self, context: bpy.types.Context):
        draw_texture_list_panel(
            self.layout,
            context.scene.saio_scene,
            "texture_world",
            False)


class SAIO_PT_ObjectTextures(PropertiesPanel):
    bl_context = "object"
    bl_label = "SAIO Object Textures"

    @classmethod
    def verify(cls, context: bpy.types.Context) -> str | None:
        if context.active_object is None:
            return "No active object"
        return None

    def draw_panel(self, context: bpy.types.Context):
        draw_texture_list_panel(
            self.layout,
            context.active_object,
            "saio_texture_world",
            True)