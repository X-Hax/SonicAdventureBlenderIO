import bpy

from ..operators import event_uv_anim_operators as uvanimop

from ...utility.draw import TOOL_PROPERTY, draw_list


EVENT_UVANIM_TOOLS: list[TOOL_PROPERTY] = [
    (
        uvanimop.SAIO_OT_Event_UVAnim_Add.bl_idname,
        "ADD",
        {}
    ),
    (
        uvanimop.SAIO_OT_Event_UVAnim_Remove.bl_idname,
        "REMOVE",
        {}
    ),
    None,
    (
        uvanimop.SAIO_OT_Event_UVAnim_Move.bl_idname,
        "TRIA_UP",
        {"direction": "UP"}
    ),
    (
        uvanimop.SAIO_OT_Event_UVAnim_Move.bl_idname,
        "TRIA_DOWN",
        {"direction": "DOWN"}
    )
]


class SAIO_UL_EventUVAnimList(bpy.types.UIList):

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

        row = layout.row()

        row.prop(
            item,
            "texture_index",
            text="Tex:",
            emboss=False)

        row.prop(
            item,
            "texture_count",
            text="Num:",
            emboss=False)


class SAIO_MT_EventUVAnimContextMenu(bpy.types.Menu):
    bl_label = "Texture list operations"

    def draw(self, context):
        layout = self.layout
        layout.operator(uvanimop.SAIO_OT_Event_UVAnim_Clear.bl_idname)


def draw_event_uv_anim_list(
        layout: bpy.types.UILayout,
        uv_animations):

    draw_list(
        layout,
        SAIO_UL_EventUVAnimList,
        SAIO_MT_EventUVAnimContextMenu,
        uv_animations,
        EVENT_UVANIM_TOOLS,
        None)
