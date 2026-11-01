import os
import bpy
from bpy.props import StringProperty, BoolProperty

from ...exceptions import SAIOUserException


class SAIOBaseOperator(bpy.types.Operator):

    def _invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        return self._execute(context)

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        try:
            return self._invoke(context, event)
        except SAIOUserException as e:
            self.report({'ERROR'}, e.message)
            return {'CANCELLED'}

    def _execute(self, context: bpy.types.Context):
        return {'FINISHED'}

    def execute(self, context):
        try:
            return self._execute(context)
        except SAIOUserException as e:
            self.report({'ERROR'}, e.message)
            return {'CANCELLED'}


class SAIOBaseModalOperator(SAIOBaseOperator):

    def _modal(self, context, event):
        self._execute(context)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        try:
            return self._modal(context, event)
        except SAIOUserException as e:
            self.report({'ERROR'}, e.message)
            return {'CANCELLED'}

    def _invoke(self, context, event):
        return {'RUNNING_MODAL'}


class SAIOBasePopupOperator(SAIOBaseOperator):

    def _invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        return context.window_manager.invoke_props_dialog(self)


class SAIOBaseFileLoadOperator(SAIOBaseOperator):

    filepath: StringProperty(
        name="File Path",
        description="Filepath used for importing the file",
        maxlen=1024,
        subtype='FILE_PATH',
        options={'HIDDEN'},
    )

    directory: StringProperty(
        name="Directory",
        description="Directory path used for importing the file(s)",
        maxlen=1024,
        subtype='DIR_PATH',
        options={'HIDDEN'},
    )

    directory_mode: BoolProperty(
        name="Directory mode",
        description="Choose a directory to save in, instead of a file",
        default=False,
        options={'HIDDEN'}
    )

    def correct_filepath(self, context: bpy.types.Context):
        if not self.directory_mode:
            return False

        if self.directory:
            filepath = self.directory + os.sep
        elif context.blend_data.filepath:
            filepath = os.path.dirname(context.blend_data.filepath) + os.sep
        else:
            return False

        changed = filepath != self.filepath
        self.filepath = filepath
        return changed

    def _invoke(self, context, event):
        self.correct_filepath(context)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def check(self, context: bpy.types.Context) -> bool:
        return self.correct_filepath(context)

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

    def get_files(self):
        if len(os.path.basename(self.filepath)) == 0:
            raise SAIOUserException("No file selected!")
        return [os.path.join(self.directory, file.name) for file in self.files]


class SAIOBaseFileSaveOperator(SAIOBaseOperator):

    filepath: StringProperty(
        name="File Path",
        description="Filepath used for exporting the file",
        maxlen=1024,
        subtype='FILE_PATH',
        options={'HIDDEN'},
    )

    directory: StringProperty(
        name="Directory",
        description="Directory path used for exporting the file(s)",
        maxlen=1024,
        subtype='DIR_PATH',
        options={'HIDDEN'},
    )

    check_existing: BoolProperty(
        name="Check Existing",
        description="Check and warn on overwriting existing files",
        default=True,
        options={'HIDDEN'},
    )

    directory_mode: BoolProperty(
        name="Directory mode",
        description="Choose a directory to save in, instead of a file",
        default=False,
        options={'HIDDEN'}
    )

    def correct_filepath(self, context: bpy.types.Context):
        if self.directory_mode:
            if self.directory:
                filepath = self.directory + os.sep
            elif context.blend_data.filepath:
                filepath = os.path.dirname(context.blend_data.filepath) + os.sep
            else:
                filepath = os.path.abspath("") + os.sep

        else:
            filepath = self.filepath
            filename = os.path.basename(filepath)
            if not filename:
                filepath = context.blend_data.filepath
                if not filepath:
                    filepath = os.path.abspath("untitled")
                else:
                    filepath = os.path.splitext(filepath)[0]

            filepath = bpy.path.ensure_ext(
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

    def check(self, context: bpy.types.Context) -> bool:
        return self.correct_filepath(context)

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False