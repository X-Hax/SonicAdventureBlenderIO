import bpy
from bpy.props import (
    BoolProperty,
    StringProperty,
)
from bpy.types import Context

from .base_export_operators import (
    ExportModelOperator,
    NodeAnimExportOperator
)


class ExportMDLOperator(ExportModelOperator):

    apply_posing: BoolProperty(
        name="Apply Armature Posing",
        description=(
            "Keep armature pose on export. Will export in rest pose by default"
        ),
        default=False
    )

    nj_file: BoolProperty(
        name="NJ File",
        description="Export as an NJ file",
        default=False
    )

    auto_root: BoolProperty(
        name="Automatic root",
        description=(
            "Creates a root on export when the objects to export are not in a"
            " shared hierarchy"
        ),
        default=True
    )

    force_sort_bones: BoolProperty(
        name="Force sort bones",
        description=(
            "Blender doesnt sort bones by name, although this may be desired"
            " in certain scenarios. This ensure the bones are sorted by name"),
        default=False
    )

    debug_output: BoolProperty(
        name="Developer tool: Debug output",
        description=(
            "Outputs the raw exported model data as a json file for debugging."
            " DONT TOUCH IF YOU ARE NOT A DEVELOPER FOR THE SAIO ADDON! It"
            " will dramatically increase export time!"),
        default=False
    )

    filename_ext = ".nj"

    @classmethod
    def poll(cls, context: Context):
        return context.mode == 'OBJECT'

    def check(self, context: Context) -> bool:
        import os
        no_ext, old_extension = os.path.splitext(self.filepath)

        extension = old_extension

        if self.nj_file:
            if old_extension != ".nj":
                extension = ".nj"
        else:
            if old_extension != self.model_file_extension:
                extension = self.model_file_extension

        if extension != old_extension:
            self.filepath = no_ext + extension
            return True

        return False

    def export_models(self, context, objects):
        from ...exporting.o_model import ModelEvaluator
        evaluator = ModelEvaluator(
            context,
            self.format,
            self.auto_root,
            self.optimize,
            self.ignore_weights,
            self.write_specular,
            self.apply_modifs,
            self.apply_posing,
            self.auto_node_attributs,
            self.force_sort_bones)

        data = evaluator.evaluate(objects)

        from SA3D.Modeling.ObjectData import MetaData, ModelFile

        metadata = MetaData()
        metadata.Author = context.scene.saio_scene.author
        metadata.Description = context.scene.saio_scene.description

        bytes = ModelFile.Write(
            self.nj_file,
            data.outdata,
            metadata)

        from System.IO import File
        File.WriteAllBytes(self.filepath, bytes)

        if self.debug_output:
            evaluator.save_debug(self.filepath + ".json")

        return {'FINISHED'}


class SAIO_OT_Export_SA1MDL(ExportMDLOperator):
    bl_idname = "saio.export_sa1mdl"
    bl_label = "SA1 model (.sa1mdl)"
    bl_description = "Exports scene or selected items to an sa1mdl file."

    model_file_extension = ".sa1mdl"

    filter_glob: StringProperty(
        default="*.sa1mdl;*.nj;",
        options={'HIDDEN'},
    )

    format = "SA1"
    ignore_weights = True
    write_specular = True


class SAIO_OT_Export_SA2MDL(ExportMDLOperator):
    bl_idname = "saio.export_sa2mdl"
    bl_label = "SA2 model (.sa2mdl)"
    bl_description = "Exports scene or selected items to an sa2mdl file."

    model_file_extension = ".sa2mdl"

    filter_glob: StringProperty(
        default="*.sa2mdl;*.nj;",
        options={'HIDDEN'},
    )

    format = "SA2"
    ignore_weights = False

    write_specular: BoolProperty(
        name="Write Specular",
        description="Write specular info to materials",
        default=False
    )


class SAIO_OT_Export_SA2BMDL(ExportMDLOperator):
    bl_idname = "saio.export_sa2bmdl"
    bl_label = "SA2B model (.sa2bmdl)"
    bl_description = "Exports scene or selected items to an sa2bmdl file."

    model_file_extension = ".sa2bmdl"

    filter_glob: StringProperty(
        default="*.sa2bmdl;*.nj;",
        options={'HIDDEN'},
    )

    format = "SA2B"
    ignore_weights = True
    write_specular = False

###############################################


class ExportLVLOperator(ExportModelOperator):

    fallback_surface_attributes: BoolProperty(
        name="Fallback surface attributes",
        description=(
            "Any land entry with no surface attributes at all received"
            " \"Visible\" and \"Solid\""
        ),
        default=True
    )

    def export_models(self, context, objects):
        from ...exporting import o_landtable

        evaluator = o_landtable.LandtableEvaluator(
            context,
            self.format,
            self.optimize,
            self.write_specular,
            self.apply_modifs,
            self.fallback_surface_attributes,
            self.auto_node_attributs)

        evaluator.evaluate(objects)
        evaluator.export(self.filepath)

        return {'FINISHED'}


class SAIO_OT_Export_SA1LVL(ExportLVLOperator):
    bl_idname = "saio.export_sa1lvl"
    bl_label = "SA1 Landtable (.sa1lvl)"
    bl_description = "Exports scene or selected items to an sa1lvl file."

    filename_ext = ".sa1lvl"

    filter_glob: StringProperty(
        default="*.sa1lvl;*.nj;",
        options={'HIDDEN'},
    )

    format = 'SA1'
    write_specular = True


class SAIO_OT_Export_SA2LVL(ExportLVLOperator):
    bl_idname = "saio.export_sa2lvl"
    bl_label = "SA2 Landtable (.sa2lvl)"
    bl_description = "Exports scene or selected items to an sa2lvl file."

    filename_ext = ".sa2lvl"

    filter_glob: StringProperty(
        default="*.sa2lvl;",
        options={'HIDDEN'},
    )

    format = 'SA2'

    write_specular: BoolProperty(
        name="Write Specular",
        description="Write specular info to materials",
        default=False
    )


class SAIO_OT_Export_SA2BLVL(ExportLVLOperator):
    bl_idname = "saio.export_sa2blvl"
    bl_label = "SA2B Landtable (.sa2blvl)"
    bl_description = "Exports scene or selected items to an sa2blvl file."

    filename_ext = ".sa2blvl"

    filter_glob: StringProperty(
        default="*.sa2blvl;",
        options={'HIDDEN'},
    )

    format = 'SA2B'
    write_specular = False

###############################################


class SAIO_OT_Export_Event(NodeAnimExportOperator):
    bl_idname = "saio.export_event"
    bl_label = "SA2 Event (.prs)"
    bl_description = "Exports the event"

    show_bone_localspace = False

    optimize: BoolProperty(
        name="Optimize",
        description="Optimize if possible",
        default=True,
    )

    auto_node_attributes: BoolProperty(
        name="Automatic Node Attributes",
        description=(
            "Automaticall determine node attributes for the exported model"
        ),
        default=True
    )

    export_textures: BoolProperty(
        name="Export texture file",
        description=(
            "Exports the texture list to a file. Maybe you dont need to do so,"
            " as you just reuse the original event textures, so not exporting"
            " it could save time."
        ),
        default=True
    )

    filename_ext = ".prs"

    filter_glob: StringProperty(
        default="*.prs;",
        options={'HIDDEN'},
    )

    def draw(self, context: bpy.types.Context):
        self.layout.prop(self, "optimize")
        self.layout.prop(self, "auto_node_attributes")
        self.layout.prop(self, "export_textures")

        return super().draw(context)

    def export(self, context: bpy.types.Context):
        from ...exporting import o_event

        anim_parameters = self.get_anim_parameters()
        anim_parameters.bone_localspace = False

        exporter = o_event.EventExporter(
            context,
            self.optimize,
            self.auto_node_attributes,
            anim_parameters)

        exporter.process()
        exporter.export(self.filepath, self.export_textures)

        return {'FINISHED'}
