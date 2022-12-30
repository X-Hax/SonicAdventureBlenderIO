import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import (
    BoolProperty,
    StringProperty,
    EnumProperty
)

from ...utils import get_default_path
from ...library import export


def _collect_objects(mode: str, context: bpy.types.Context):

    def check(x: bpy.types.Object): return True

    if mode == 'VISIBLE':
        def check(x: bpy.types.Object): return not x.hide_get()
    elif mode == 'SELECTED':
        def check(x: bpy.types.Object): return x.select_get()

    return [obj for obj in context.scene.objects if check(obj)]


class ExportOperator(bpy.types.Operator, ExportHelper):
    bl_options = {'PRESET', 'UNDO'}

    select_mode: EnumProperty(
        name="Select mode",
        description="Which objects to select for export",
        items=(
            ("ALL", "All", "All objects in the scene"),
            ("VISIBLE", "Visible", "Visible objects only"),
            ("SELECTED", "Selected", "Selected objects only")
        ),
        default="ALL"
    )

    apply_modifs: BoolProperty(
        name="Apply Modifiers",
        description="Apply active viewport modifiers",
        default=True,
    )

    optimize: BoolProperty(
        name="Optimize",
        description="Optimize if possible",
        default=True,
    )

    # console_debug_output: BoolProperty(
    #     name="Console Output",
    #     description=(
    #         "Shows exporting progress in Console"
    #         " (Slows down Exporting Immensely)"
    #     ),
    #     default=False,
    # )

    # profile_output: BoolProperty(
    #     name="Profiling output",
    #     description=(
    #         "Records where the addon spends most of"
    #         " its time and writes it to a file next"
    #         " to the actual output file"
    #     ),
    #     default=False
    # )

    def draw_options(self, context):
        layout = self.layout
        layout.prop(self, "select_mode")
        layout.prop(self, "apply_modifs")
        layout.prop(self, "optimize")

    def draw_debug(self, context):
        layout = self.layout
        # layout.separator()
        # layout.prop(self, "console_debug_output")
        # layout.prop(self, "profile_output")

    def draw(self, context):
        self.layout.alignment = 'RIGHT'

        self.draw_options(context)
        self.draw_debug(context)

    def export(self, context, objects):
        return {'FINISHED'}

    def execute(self, context):
        objects = _collect_objects(self.select_mode, context)
        return self.export(context, objects)

    def invoke(self, context, event):
        self.filepath = get_default_path(context)
        wm = context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class ExportModelOperator(ExportOperator):

    nj_file: BoolProperty(
        name="NJ File",
        description="Export as an NJ file",
        default=False
    )

    def draw_options(self, context):
        super().draw_options(context)
        self.layout.prop(self, "nj_file")


class SAIO_OT_Export_SA1MDL(ExportModelOperator):
    bl_idname = "saio.export_sa1mdl"
    bl_label = "SA1 model (.sa1mdl)"
    bl_description = "Exports scene or selected items to an sa1mdl file."

    filename_ext = ".sa1mdl"

    filter_glob: StringProperty(
        default="*.sa1mdl;",
        options={'HIDDEN'},
    )

    def export(self, context, objects):
        export.export_model(
            context,
            objects,
            'SA1',
            self.filepath,
            self.nj_file,
            self.optimize,
            True,
            True,
            self.apply_modifs)
        return {'FINISHED'}


class SAIO_OT_Export_SA2MDL(ExportModelOperator):
    bl_idname = "saio.export_sa2mdl"
    bl_label = "SA2 model (.sa2mdl)"
    bl_description = "Exports scene or selected items to an sa2mdl file."

    filename_ext = ".sa2mdl"

    filter_glob: StringProperty(
        default="*.sa2mdl;",
        options={'HIDDEN'},
    )

    write_specular: BoolProperty(
        name="Write Specular",
        description="Write specular info to materials",
        default=False
    )

    def draw_options(self, context):
        super().draw_options(context)
        self.layout.prop(self, "write_specular")

    def export(self, context, objects):
        export.export_model(
            context,
            objects,
            'SA2',
            self.filepath,
            self.nj_file,
            self.optimize,
            False,
            self.write_specular,
            self.apply_modifs)
        return {'FINISHED'}


class SAIO_OT_Export_SA2BMDL(ExportModelOperator):
    bl_idname = "saio.export_sa2bmdl"
    bl_label = "SA2B model (.sa2bmdl)"
    bl_description = "Exports scene or selected items to an sa2bmdl file."

    filename_ext = ".sa2bmdl"

    filter_glob: StringProperty(
        default="*.sa2bmdl;",
        options={'HIDDEN'},
    )

    def export(self, context, objects):
        export.export_model(
            context,
            objects,
            'SA2B',
            self.filepath,
            self.nj_file,
            self.optimize,
            True,
            False,
            self.apply_modifs)
        return {'FINISHED'}


class SAIO_OT_Export_SA1LVL(ExportOperator):
    bl_idname = "saio.export_sa1lvl"
    bl_label = "SA1 level (.sa1lvl)"
    bl_description = "Exports scene or selected items to an sa1lvl file."

    filename_ext = ".sa1lvl"

    filter_glob: StringProperty(
        default="*.sa1lvl;",
        options={'HIDDEN'},
    )


class SAIO_OT_Export_SA2LVL(ExportOperator):
    bl_idname = "saio.export_sa2lvl"
    bl_label = "SA2 level (.sa2lvl)"
    bl_description = "Exports scene or selected items to an sa2lvl file."

    filename_ext = ".sa2lvl"

    filter_glob: StringProperty(
        default="*.sa2lvl;",
        options={'HIDDEN'},
    )

    write_Specular: BoolProperty(
        name="Write Specular",
        description="Write specular info to materials",
        default=False
    )

    def draw_options(self, context):
        super().draw_options(context)
        self.layout.prop(self, "write_specular")


class SAIO_OT_Export_SA2BLVL(ExportOperator):
    bl_idname = "saio.export_sa2blvl"
    bl_label = "SA2B level (.sa2blvl)"
    bl_description = "Exports scene or selected items to an sa2blvl file."

    filename_ext = ".sa2blvl"

    filter_glob: StringProperty(
        default="*.sa2blvl;",
        options={'HIDDEN'},
    )
