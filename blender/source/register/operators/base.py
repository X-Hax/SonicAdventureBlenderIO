import os
import bpy
from bpy.props import EnumProperty, StringProperty, BoolProperty
from bpy.types import Context, Event
from bpy_extras.io_utils import ExportHelper, ImportHelper

from ...exceptions import UserException


class SAIOBaseOperator(bpy.types.Operator):

    def _invoke(self, context: Context, event: Event):  # pylint: disable=unused-argument
        return self._execute(context)

    def invoke(self, context: Context, event: Event):
        try:
            return self._invoke(context, event)
        except UserException as e:
            self.report({'ERROR'}, e.message)
            return {'CANCELLED'}

    def _execute(self, context: bpy.types.Context):  # pylint: disable=unused-argument
        return {'FINISHED'}

    def execute(self, context):
        try:
            return self._execute(context)
        except UserException as e:
            self.report({'ERROR'}, e.message)
            return {'CANCELLED'}


class SAIOBasePopupOperator(SAIOBaseOperator):

    def _invoke(self, context: Context, event: Event):
        return context.window_manager.invoke_props_dialog(self)


class SAIOBaseFileLoadOperator(SAIOBaseOperator):

    filepath: StringProperty(
        name="File Path",
        description="Filepath used for importing the file",
        maxlen=1024,
        subtype='FILE_PATH',
    )

    def _invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def draw(self, context: Context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.


class SAIOBaseFileSaveOperator(SAIOBaseOperator):

    filepath: StringProperty(
        name="File Path",
        description="Filepath used for exporting the file",
        maxlen=1024,
        subtype='FILE_PATH',
        options={'HIDDEN'},
    )

    check_existing: BoolProperty(
        name="Check Existing",
        description="Check and warn on overwriting existing files",
        default=True,
        options={'HIDDEN'},
    )

    def correct_filepath(self, context: bpy.types.Context):
        filepath = self.filepath
        if not filepath:
            filepath = context.blend_data.filepath
            if not filepath:
                filepath = "untitled"
            else:
                filepath = os.path.splitext(filepath)[0]

        filepath = bpy.path.ensure_ext(  # pylint: disable=assignment-from-no-return
            os.path.splitext(filepath)[0],
            self.filename_ext,
        )

        changed = filepath != self.filepath
        self.filepath = filepath
        return changed

    def _invoke(self, context, event):
        self.correct_filepath(context)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def check(self, context: Context) -> bool:
        return self.correct_filepath(context)

    def draw(self, context: Context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.


class ListAdd:

    def list_execute(self, context, target_list):  # pylint: disable=unused-argument
        target_list.new()


class ListRemove:

    def list_execute(self, context, target_list):  # pylint: disable=unused-argument
        target_list.remove(target_list.active_index)


class ListMove:

    direction: EnumProperty(
        name="Direction",
        items=(
            ('UP', "up", "up"),
            ('DOWN', "down", "down"),
        )
    )

    def list_execute(self, context, target_list):  # pylint: disable=unused-argument
        old_index = target_list.active_index

        if old_index == -1:
            return

        new_index = (
            target_list.active_index
            + (-1 if self.direction == 'UP'
                else 1)
        )

        if new_index < 0 or new_index >= len(target_list):
            return

        target_list.move(
            old_index,
            new_index)


class ListClear:
    def list_execute(self, context, target_list):  # pylint: disable=unused-argument
        target_list.clear()
