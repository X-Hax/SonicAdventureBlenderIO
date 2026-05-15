import bpy

from .base_panel import PropertiesPanel

from ..operators import texture_operators as texop

from ...utility.draw import draw_list, TOOL_PROPERTY


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
        mode_op(texop.SAIO_OT_Textures_Import_Pack.bl_idname)
        layout.separator()
        mode_op(texop.SAIO_OT_Textures_Export_Archive.bl_idname)
        mode_op(texop.SAIO_OT_Textures_Export_Pack.bl_idname)
        layout.separator()
        mode_op(texop.SAIO_OT_Texture_ToAssetLibrary.bl_idname)


class SAIO_MT_TextureContextMenuScene(BaseTextureContextMenu):
    texture_mode = 'SCENE'

class SAIO_MT_TextureContextMenuObject(BaseTextureContextMenu):
    texture_mode = 'OBJECT'

def draw_texture_list_panel(
        layout: bpy.types.UILayout,
        world_container: any,
        world_prop_name: str,
        is_object: bool):

    layout.template_ID(world_container, world_prop_name, new="world.new")
    world = getattr(world_container, world_prop_name)

    if world is None:
        return

    texture_list = world.saio_texture_list

    def set_op(operator, i): # pylint: disable=unused-argument
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
        texture = texture_list[
            texture_list.active_index]

        layout.prop_search(texture, "image", bpy.data, "images")
        layout.prop(texture, "name")
        layout.prop(texture, "global_index")
        layout.separator()
        layout.prop(texture, "override_width")
        layout.prop(texture, "override_height")
        layout.prop(texture, "texture_type")


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
