import bpy

from .base_panel import PropertiesPanel

from ..operators import event_node_uv_anim_operators as uvanimop
from ..property_groups.scene_properties import SAIO_Scene

from ...utility.draw import draw_list, TOOL_PROPERTY

EVENT_NODE_UVANIM_TOOLS: list[TOOL_PROPERTY] = [
    (
        uvanimop.SAIO_OT_EventNode_UVAnim_Add.bl_idname,
        "ADD",
        {}
    ),
    (
        uvanimop.SAIO_OT_EventNode_UVAnim_Remove.bl_idname,
        "REMOVE",
        {}
    ),
    None,
    (
        uvanimop.SAIO_OT_EventNode_UVAnim_Move.bl_idname,
        "TRIA_UP",
        {"direction": "UP"}
    ),
    (
        uvanimop.SAIO_OT_EventNode_UVAnim_Move.bl_idname,
        "TRIA_DOWN",
        {"direction": "DOWN"}
    )
]


class SAIO_UL_EventNodeUVAnimList(bpy.types.UIList):

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

        layout.prop(
            item,
            "material_index",
            text="",
            emboss=False)


class SAIO_MT_EventNodeUVAnimContextMenu(bpy.types.Menu):
    bl_label = "Texture list operations"

    def draw(self, context):
        layout = self.layout
        layout.operator(uvanimop.SAIO_OT_EventNode_UVAnim_Clear.bl_idname)


class SAIO_PT_EventNodeUVAnimPanel(PropertiesPanel):
    bl_context = "object"
    bl_label = "SAIO Event Node UV Animations"

    @staticmethod
    def draw_node_uv_anim_list(
            layout: bpy.types.UILayout,
            event_node_uv_animations):

        layout.label(text="Indices of Materials to animate:")

        draw_list(
            layout,
            SAIO_UL_EventNodeUVAnimList,
            SAIO_MT_EventNodeUVAnimContextMenu,
            event_node_uv_animations,
            EVENT_NODE_UVANIM_TOOLS,
            None)

    # === overriden methods === #

    @classmethod
    def verify(cls, context: bpy.types.Context):
        error = SAIO_Scene.check_is_event(context)
        if error is not None:
            return error

        if context.active_object is None:
            return "No active object"

        object = context.active_object
        if object.type != 'MESH':
            return "Object not a Mesh"

        return None

    def draw_panel(self, context: bpy.types.Context):

        SAIO_PT_EventNodeUVAnimPanel.draw_node_uv_anim_list(
            self.layout,
            context.active_object.saio_eventnode_uvanims)
