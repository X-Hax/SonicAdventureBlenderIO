import bpy
from bpy.props import (
    BoolProperty,
    StringProperty,
    EnumProperty,
    FloatProperty
)
from bpy.types import Context, UILayout

from .base_export_operators import (
    ExportModelOperator,
    NodeAnimExportOperator
)

from ...utility.anim_parameters import AnimParameters
from ...dotnet import SA3D_Modeling


class ExportMDLOperator(ExportModelOperator):

    filename_ext = ".nj"
    model_file_extension: str
    flip_vertex_color_channels: bool = False

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

    def draw_panel_general(self, layout: UILayout):
        body = super().draw_panel_general(layout)

        if body:
            body.prop(self, "apply_posing")

        return body

    def draw_other(self, layout: UILayout, is_file_browser: bool):
        self.draw_panel_encoding(layout)

    def draw_panel_encoding(self, layout: UILayout):
        header, body = layout.panel(
            "SAIO_export_mdl_encoding", default_closed=True)
        header.label(text="Encoding")

        if body:
            body.prop(self, "nj_file")

        return body

    def export_models(self, context, objects):
        from ...exporting.o_model import ModelEvaluator
        from ...exporting.o_enum import to_model_format

        evaluator = ModelEvaluator(
            context,
            self.format,  # pylint: disable=no-member
            self.auto_root,
            self.optimize,
            self.apply_modifs,
            self.apply_posing,
            self.auto_node_attribute_mode,
            self.force_sort_bones,
            self.flip_vertex_color_channels)  # pylint: disable=no-member

        data = evaluator.evaluate(objects)

        if self.ensure_positive_euler_angles:
            data.outdata.EnsurePositiveEulerAnglesTree()

        if self.debug_output:
            evaluator.save_debug(self.filepath + ".json")

        metadata = SA3D_Modeling.META_DATA()
        metadata.Author = context.scene.saio_scene.author
        metadata.Description = context.scene.saio_scene.description

        model_format = to_model_format(
            self.format)  # pylint: disable=no-member

        SA3D_Modeling.MODEL_FILE.WriteToFile(
            self.filepath,
            data.outdata,
            self.nj_file,
            metadata,
            model_format
        )

        return {'FINISHED'}


class SAIO_OT_Export_SA1MDL(ExportMDLOperator):
    bl_idname = "saio.export_sa1mdl"
    bl_label = "SA1 model (.sa1mdl)"
    bl_description = "Exports scene or selected items to an sa1mdl file."

    model_file_extension = ".sa1mdl"
    format = "SA1"

    filter_glob: StringProperty(
        default="*.sa1mdl;*.nj;",
        options={'HIDDEN'},
    )


class SAIO_OT_Export_SA2MDL(ExportMDLOperator):
    bl_idname = "saio.export_sa2mdl"
    bl_label = "SA2 model (.sa2mdl)"
    bl_description = "Exports scene or selected items to an sa2mdl file."

    model_file_extension = ".sa2mdl"
    format = "SA2"

    filter_glob: StringProperty(
        default="*.sa2mdl;*.nj;",
        options={'HIDDEN'},
    )

    flip_vertex_color_channels: BoolProperty(
        name="Flip vertex color channels",
        description="Flips vertex color channels from ARGB to BGRA.",
        default=False
    )

    def draw_panel_encoding(self, layout: UILayout):
        body = super().draw_panel_encoding(layout)

        if body:
            body.prop(self, "flip_vertex_color_channels")

        return body


class SAIO_OT_Export_SA2BMDL(ExportMDLOperator):
    bl_idname = "saio.export_sa2bmdl"
    bl_label = "SA2B model (.sa2bmdl)"
    bl_description = "Exports scene or selected items to an sa2bmdl file."

    model_file_extension = ".sa2bmdl"
    format = "SA2B"

    filter_glob: StringProperty(
        default="*.sa2bmdl;*.nj;",
        options={'HIDDEN'},
    )


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

    #######################################

    short_rot: BoolProperty(
        name="Use 16 bit rotations",
        description="Whether to use 16 bit BAMS for the rotation keyframes",
        default=False
    )

    rotation_mode: EnumProperty(
        name="Rotation Mode",
        description="How rotations should be exported",
        items=(
            ("EULER", "Euler", "Export rotations as euler"
                " (sonic adventure compatible)"),
            ("QUATERNION", "Quaternion", "Export rotations as quaternion"
                " (compatible with games like PSO2)"),
            ("KEEP", "Keep",
                "Export bone rotation modes"),
        ),
        default="EULER"
    )

    quaternion_threshold: FloatProperty(
        name="Quaternion conversion deviation threshold",
        description=(
            "If the animations rotation data doesnt match the export"
            " rotation mode, the data will have to be converted. converting"
            " between euler and quaternion rotations is inaccurate, as the"
            " interpolation between those types is not linear. This value"
            " determines the threshold, from which a keyframe should be"
            " removed."

            "\n0 means all interpolated keyframes, 1 means none."

            "\nUsually, a value around 0.05 is enough and gets rid of most"
            " unnecessary keyframes."

            "\nDoes not affect keyframes determined by the addon"
        ),
        min=0,
        max=1,
        default=0
    )

    quaternion_optimization_threshold: FloatProperty(
        name="Quaternion Optimization deviation threshold",
        description=(
            "Utilized for optimization of quaternions. If a keyframe deviates"
            " less than the threshold from its linear interpolated"
            " counterpart, it will be removed."

            "\n0 will not optimize at all"

            "\nAffects all frames"
        ),
        min=0,
        default=0
    )

    interpolation_threshold: FloatProperty(
        name="Interpolation conversion deviation threshold",
        description=(
            "Keyframes between non linear keyframes need to be baked for"
            " export. This factor determines that, if a keyframes deviates"
            " less than the given value from its linear interpolated"
            " counterpart, it will be removed."

            "\n0 is gonna bake every value (except for keyframes using linear"
            " or constant interpolation)."

            "\nDoes not affect manually placed keyframes"
        ),
        min=0,
        default=0,
    )

    general_optimization_threshold: FloatProperty(
        name="Optimization deviation threshold",
        description=(
            "Utilized for optimization of all but rotations. If a keyframe"
            " deviates less than the threshold from its linear interpolated"
            " counterpart, it will be removed."

            "\n0 will not optimize at all"

            "\nAffects all frames"
        ),
        min=0,
        default=0
    )

    #######################################

    multi_export = True

    def draw_other(self, layout: UILayout, is_file_browser: bool):
        self.draw_panel_landtable(layout)
        self.draw_panel_animation(layout)

    def draw_panel_landtable(self, layout: UILayout):
        header, body = layout.panel(
            "SAIO_export_lvl_landtable", default_closed=True)
        header.label(text="Landtable")

        if body:
            body.prop(self, "fallback_surface_attributes")

        return body

    def draw_panel_animation(self, layout: UILayout):
        header, body = layout.panel(
            "SAIO_export_lvl_animation", default_closed=True)
        header.label(text="Animation")

        if body:
            body.prop(self, "auto_root")
            body.prop(self, "force_sort_bones")
            body.prop(self, "short_rot")

            self.draw_panel_advanced_animation(body)

        return body

    def draw_panel_advanced_animation(self, layout: UILayout):
        header, body = layout.panel(
            "SAIO_export_lvl_advanced_animation", default_closed=True)
        header.label(text="Advanced")

        if body:
            col = body.column(heading = "General Conversion", align = True)
            col.prop(self, "interpolation_threshold")
            col.prop(self, "general_optimization_threshold")

            col = body.column(heading = "Rotation Conversion", align = True)
            col.prop(self, "rotation_mode")
            col.prop(self, "quaternion_threshold")
            col.prop(self, "quaternion_optimization_threshold")

        return body

    def get_anim_parameters(self):
        return AnimParameters(
            True,
            self.rotation_mode,
            self.interpolation_threshold,
            self.quaternion_threshold,
            self.general_optimization_threshold,
            self.quaternion_optimization_threshold,
            self.short_rot,
            self.ensure_positive_euler_angles
        )

    def export_models(self, context, objects):
        from ...exporting import o_landtable

        evaluator = o_landtable.LandtableEvaluator(
            context,
            self.format,  # pylint: disable=no-member
            self.optimize,
            self.apply_modifs,
            self.fallback_surface_attributes,
            self.auto_node_attribute_mode,
            self.auto_root,
            self.force_sort_bones,
            self.get_anim_parameters())

        evaluator.evaluate(objects)

        if self.debug_output:
            evaluator.save_debug(self.filepath + ".json")

        evaluator.export(self.filepath)
        return {'FINISHED'}


class SAIO_OT_Export_SA1LVL(ExportLVLOperator):
    bl_idname = "saio.export_sa1lvl"
    bl_label = "SA1 Landtable (.sa1lvl)"
    bl_description = "Exports scene or selected items to an sa1lvl file."

    filename_ext = ".sa1lvl"
    format = 'SA1'

    filter_glob: StringProperty(
        default="*.sa1lvl;*.nj;",
        options={'HIDDEN'},
    )


class SAIO_OT_Export_SA2LVL(ExportLVLOperator):
    bl_idname = "saio.export_sa2lvl"
    bl_label = "SA2 Landtable (.sa2lvl)"
    bl_description = "Exports scene or selected items to an sa2lvl file."

    filename_ext = ".sa2lvl"
    format = 'SA2'

    filter_glob: StringProperty(
        default="*.sa2lvl;",
        options={'HIDDEN'},
    )


class SAIO_OT_Export_SA2BLVL(ExportLVLOperator):
    bl_idname = "saio.export_sa2blvl"
    bl_label = "SA2B Landtable (.sa2blvl)"
    bl_description = "Exports scene or selected items to an sa2blvl file."

    filename_ext = ".sa2blvl"
    format = 'SA2B'

    filter_glob: StringProperty(
        default="*.sa2blvl;",
        options={'HIDDEN'},
    )


###############################################


class SAIO_OT_Export_Event(NodeAnimExportOperator):
    bl_idname = "saio.export_event"
    bl_label = "SA2 Event (.prs)"
    bl_description = "Exports the event"

    show_bone_localspace = False

    filename_ext = ".prs"

    filter_glob: StringProperty(
        default="*.prs;",
        options={'HIDDEN'},
    )

    event_type: EnumProperty(
        name="Event Type",
        description="Type of event to export",
        items=(
            ('DCBETA', "Dreamcast Beta", "Event targetting Dreamcast beta builds"),
            ('DC', "Dreamcast", "Event targetting Dreamcast"),
            ('DCGC', "Dreamcast-Gamecube",
                "Event targetting Gamecube (and ports) but with Greamcast formatting"),
            ('GC', "Gamecube", "Event targetting Gamecube and ports"),
        ),
        default='GC'
    )

    optimize: BoolProperty(
        name="Optimize",
        description="Optimize if possible",
        default=True,
    )

    auto_node_attribute_mode: EnumProperty(
        name="Automatic Node Attribute Mode",
        description=(
            "Automatically determine node attributes for the exported model"
        ),
        items=(
            ('NONE', "None", "Do no automatically evaluate node attributes"),
            ('MISSING', "Missing",
             "Automatically evaluate node attributes as well as keep those enabled in objects"),
            ('OVERRIDE', "Override",
             "Automatically evaluate node attributes and override those enabled in objects"),
        ),
        default='MISSING'
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

    def draw(self, context: Context):
        self.draw_panel_general(self.layout)
        self.draw_panel_extra(self.layout)
        super().draw(context)

    def draw_panel_general(self, layout: UILayout):
        header, body = layout.panel(
            "SAIO_export_event_general", default_closed=True)
        header.label(text="General")

        if body:
            body.prop(self, "event_type")
            body.prop(self, "optimize")
            body.prop(self, "auto_node_attribute_mode")

        return body

    def draw_panel_extra(self, layout: UILayout):
        header, body = layout.panel(
            "SAIO_export_event_extra", default_closed=True)
        header.label(text="Extra")

        if body:
            body.prop(self, "export_textures")

        return body

    def export(self, context: bpy.types.Context):
        from ...exporting import o_event

        anim_parameters = self.get_anim_parameters()
        anim_parameters.bone_localspace = False

        exporter = o_event.EventExporter(
            context,
            self.event_type,
            self.optimize,
            self.auto_node_attribute_mode,
            anim_parameters)

        exporter.process()
        exporter.export(self.filepath, self.export_textures)

        return {'FINISHED'}
