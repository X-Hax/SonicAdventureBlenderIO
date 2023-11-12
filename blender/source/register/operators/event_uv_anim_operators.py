import bpy

from .base import SAIOBaseOperator, ListAdd, ListRemove, ListMove, ListClear


class EventUVAnimOperator(SAIOBaseOperator):
    bl_options = {'UNDO'}

    def _execute(self, context: bpy.types.Context):
        anims = context.scene.saio_scene.event.uv_animations
        self.list_execute(context, anims)  # pylint: disable=no-member
        return {'FINISHED'}


class SAIO_OT_Event_UVAnim_Add(EventUVAnimOperator, ListAdd):
    bl_idname = "saio.event_uvanims_add"
    bl_label = "Add UV Animation"
    bl_description = "Adds a UV Animation to the UV Animation list"


class SAIO_OT_Event_UVAnim_Remove(EventUVAnimOperator, ListRemove):
    bl_idname = "saio.event_uvanims_remove"
    bl_label = "Remove UV Animation"
    bl_description = (
        "Removes the selected UV Animation from the UV Animation list"
    )


class SAIO_OT_Event_UVAnim_Move(EventUVAnimOperator, ListMove):
    bl_idname = "saio.event_uvanims_move"
    bl_label = "Move UV Animation"
    bl_description = "Moves UV Animation slot in list"


class SAIO_OT_Event_UVAnim_Clear(EventUVAnimOperator, ListClear):
    bl_idname = "saio.event_uvanims_clear"
    bl_label = "Clear list"
    bl_description = "Removes all entries from the list"
