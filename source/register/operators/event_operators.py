import bpy

from .base import SAIOBaseOperator, ListAdd, ListRemove, ListMove, ListClear


class EventSceneListOperator(SAIOBaseOperator):
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.scene.saio_scene.scene_type == 'EVR'

    def _execute(self, context):
        self.list_execute(context, context.scene.saio_scene.event)
        return {'FINISHED'}


class SAIO_OT_EventScene_Add(EventSceneListOperator, ListAdd):
    bl_idname = "saio.eventscene_add"
    bl_label = "Add scene"
    bl_description = "Adds scene to the scene list"


class SAIO_OT_EventScene_Remove(EventSceneListOperator, ListRemove):
    bl_idname = "saio.eventscene_remove"
    bl_label = "Remove scene"
    bl_description = "Removes the selected scene from the texture list"


class SAIO_OT_EventScene_Move(EventSceneListOperator, ListMove):
    bl_idname = "saio.eventscene_move"
    bl_label = "Move scene"
    bl_description = "Moves scene slot in list"


class SAIO_OT_EventScene_Clear(EventSceneListOperator, ListClear):
    bl_idname = "saio.eventscene_clear"
    bl_label = "Clear list"
    bl_description = "Removes all entries from the list"
