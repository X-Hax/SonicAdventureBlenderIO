import bpy

from .base_panel import PropertiesPanel

from ..operators import texture_name_operators as texnamop

from ...utility.draw import draw_list, TOOL_PROPERTY

TEXTURENAMELIST_TOOLS: list[TOOL_PROPERTY] = [
    (
        texnamop.SAIO_OT_TextureNames_Add.bl_idname,
        "ADD",
        {}
    ),
    (
        texnamop.SAIO_OT_TextureNames_Remove.bl_idname,
        "REMOVE",
        {}
    ),
    None,
    (
        texnamop.SAIO_OT_TextureNames_Move.bl_idname,
        "TRIA_UP",
        {"direction": "UP"}
    ),
    (
        texnamop.SAIO_OT_TextureNames_Move.bl_idname,
        "TRIA_DOWN",
        {"direction": "DOWN"}
    )
]


class SAIO_UL_TextureNameList(bpy.types.UIList):

    def draw_item( # pylint: disable=signature-differs
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

        layout.prop(
            item,
            "name",
            text=str(index),
            emboss=False)


class BaseTextureNameContextMenu(bpy.types.Menu):
    bl_label = "Texture list operations"

    def draw(self, context):
        layout = self.layout

        def mode_op(bl_idname: str):
            op = layout.operator(bl_idname)
            op.mode = self.texture_mode

        mode_op(texnamop.SAIO_OT_TextureNames_Clear.bl_idname)
        layout.separator()
        mode_op(texnamop.SAIO_OT_TextureNames_Import.bl_idname)
        mode_op(texnamop.SAIO_OT_TextureNames_Export.bl_idname)

class SAIO_MT_TextureNameContextMenuScene(BaseTextureNameContextMenu):
    texture_mode = 'SCENE'

class SAIO_MT_TextureNameContextMenuObject(BaseTextureNameContextMenu):
    texture_mode = 'OBJECT'


@staticmethod
def draw_texture_name_list_panel(
        layout: bpy.types.UILayout,
        world_container: any,
        world_prop_name: str,
        is_object: bool):

    layout.template_ID(world_container, world_prop_name, new="world.new")
    world = getattr(world_container, world_prop_name)

    if world is None:
        return

    texturename_list = world.saio_texturename_list

    def set_op(operator, i): # pylint: disable=unused-argument
        if is_object:
            operator.mode = "OBJECT"

    draw_list(
        layout,
        SAIO_UL_TextureNameList,
        SAIO_MT_TextureNameContextMenuObject if is_object else SAIO_MT_TextureNameContextMenuScene,
        texturename_list,
        TEXTURENAMELIST_TOOLS,
        set_op
    )


class SAIO_PT_SceneTexturenames(PropertiesPanel):
    bl_context = "scene"
    bl_label = "SAIO Scene Texture Names"

    def draw_panel(self, context: bpy.types.Context):
        draw_texture_name_list_panel(
            self.layout,
            context.scene.saio_scene,
            "texturename_world",
            False)


class SAIO_PT_ObjectTexturenames(PropertiesPanel):
    bl_context = "object"
    bl_label = "SAIO Object Texture Names"

    @classmethod
    def verify(cls, context: bpy.types.Context) -> str | None:
        if context.active_object is None:
            return "No active object"
        return None

    def draw_panel(self, context: bpy.types.Context):
        draw_texture_name_list_panel(
            self.layout,
            context.active_object,
            "saio_texturename_world",
            True)
