import bpy

from .base import SAIOBaseOperator, ListAdd, ListRemove, ListMove, ListClear


class EventNodeUVAnimOperator(SAIOBaseOperator):
    bl_options = {'UNDO'}

    def _execute(self, context: bpy.types.Context):
        anims = context.active_object.saio_eventnode_uvanims
        self.list_execute(context, anims)  # pylint: disable=no-member
        return {'FINISHED'}


class SAIO_OT_EventNode_UVAnim_Add(EventNodeUVAnimOperator, ListAdd):
    bl_idname = "saio.eventnode_uvanims_add"
    bl_label = "Add UV Animation"
    bl_description = "Adds a UV Animation to the UV Animation list"


class SAIO_OT_EventNode_UVAnim_Remove(EventNodeUVAnimOperator, ListRemove):
    bl_idname = "saio.eventnode_uvanims_remove"
    bl_label = "Remove UV Animation"
    bl_description = (
        "Removes the selected UV Animation from the UV Animation list"
    )


class SAIO_OT_EventNode_UVAnim_Move(EventNodeUVAnimOperator, ListMove):
    bl_idname = "saio.eventnode_uvanims_move"
    bl_label = "Move UV Animation"
    bl_description = "Moves UV Animation slot in list"


class SAIO_OT_EventNode_UVAnim_Clear(EventNodeUVAnimOperator, ListClear):
    bl_idname = "saio.eventnode_uvanims_clear"
    bl_label = "Clear list"
    bl_description = "Removes all entries from the list"
