import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    StringProperty
)
from bpy.types import Context, UILayout
from .base import SAIOBaseFileSaveOperator
from ...utility.anim_parameters import AnimParameters


class ExportOperator(SAIOBaseFileSaveOperator):
    bl_options = {'PRESET', 'UNDO'}

    def export(self, context: bpy.types.Context):  # pylint: disable=unused-argument
        return {'FINISHED'}

    def _execute(self, context):
        from os import path
        if len(self.filepath) == 0 or self.filepath.endswith(path.sep):
            self.filepath += "unnamed" + self.filename_ext

        from ...dotnet import load_dotnet
        load_dotnet()

        return self.export(context)


class ExportModelOperator(ExportOperator):

    use_selection: BoolProperty(
        name='Selected Objects',
        description='Export selected objects only',
        default=False
    )

    use_visible: BoolProperty(
        name='Visible Objects',
        description='Export visible objects only',
        default=False
    )

    use_active_collection: BoolProperty(
        name='Active Collection',
        description='Export objects in the active collection only',
        default=False
    )

    use_active_scene: BoolProperty(
        name='Active Scene',
        description='Export active scene only',
        default=False
    )

    collection: StringProperty(
        name="Source Collection",
        description="Export only objects from this collection (and its children)",
        default="",
    )

    apply_modifs: BoolProperty(
        name="Apply Modifiers",
        description="Apply active viewport modifiers",
        default=True,
    )

    optimize: BoolProperty(
        name="Optimize",
        description="Optimize if possible",
        default=False,
    )

    auto_root: BoolProperty(
        name="Automatic root",
        description=(
            "Creates a root on export when the objects to export are not in a"
            " shared hierarchy"
        ),
        default=True
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

    ensure_positive_euler_angles: BoolProperty(
        name="Ensure positive euler angles",
        description="Ensure that all exported euler rotation angles are positive.",
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

    multi_export = False

    def export_models(self, context, objects):  # pylint: disable=unused-argument
        return {'FINISHED'}

    @staticmethod
    def _collect_objects(mode: str, context: bpy.types.Context, multi_export: bool):

        if mode == 'VISIBLE':
            def check(x: bpy.types.Object):
                return not x.hide_get()
        elif mode == 'SELECTED':
            def check(x: bpy.types.Object):
                return x.select_get()
        else:
            def check(x: bpy.types.Object):  # pylint: disable=unused-argument
                return True

        result = {obj for obj in context.scene.objects if check(obj)}

        roots = set()
        for obj in result:
            parent = obj
            while parent.parent is not None:
                parent = parent.parent
            roots.add(parent)

        if len(roots) == 1 or multi_export:
            for root in roots:
                if root.type == 'ARMATURE':
                    result.add(root)

        return result

    def export(self, context):
        objects = ExportModelOperator._collect_objects(
            self.select_mode, context, self.multi_export)
        return self.export_models(context, objects)

    def draw(self, context: Context):
        super().draw(context)
        layout = self.layout

        # Are we inside the File browser
        is_file_browser = context.space_data.type == 'FILE_BROWSER'

        self.draw_panel_include(layout, is_file_browser)
        self.draw_panel_general(layout)
        self.draw_other(layout, is_file_browser)
        self.draw_panel_debug(layout)

    def draw_panel_include(self, layout: UILayout, is_file_browser: bool):
        if is_file_browser:
            return

        header, body = layout.panel(
            "SAIO_export_model_include", default_closed=True)
        header.label(text="Include")

        if body:
            col = body.column(heading="Limit to", align=True)
            col.prop(self, "use_selection")
            col.prop(self, "use_visible")
            col.prop(self, "use_active_collection")
            col.prop(self, "use_active_scene")

        return body

    def draw_panel_general(self, layout: UILayout):
        header, body = layout.panel(
            "SAIO_export_model_general", default_closed=True)
        header.label(text="General")

        if body:
            body.prop(self, "apply_modifs")
            body.prop(self, "optimize")
            body.prop(self, "auto_root")
            body.prop(self, "auto_node_attribute_mode")
            body.prop(self, "ensure_positive_euler_angles")
            body.prop(self, "force_sort_bones")

        return body

    def draw_other(self, layout: UILayout, is_file_browser: bool):
        return

    def draw_panel_debug(self, layout: UILayout):
        header, body = layout.panel(
            "SAIO_export_model_debug", default_closed=True)
        header.label(text="Debug")

        if body:
            body.prop(self, "debug_output")

        return body


class AnimationExportOperator(ExportOperator):

    filename_ext = ".saanim"

    filter_glob: StringProperty(
        default="*.saanim;",
        options={'HIDDEN'},
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

    def get_anim_parameters(self):
        return AnimParameters(
            True,
            "KEEP",
            self.interpolation_threshold,
            0,
            self.general_optimization_threshold,
            0
        )

    def draw(self, context: bpy.types.Context):
        super().draw(context)
        layout = self.layout

        self.draw_other(layout)
        self.draw_panel_advanced(layout)

    def draw_other(self, layout):
        return

    def draw_panel_advanced(self, layout: UILayout):
        header, body = layout.panel(
            "SAIO_export_anim_advanced", default_closed=True)
        header.label(text="Advanced")

        if body:
            col = body.column(heading = "General Conversion", align = True)
            col.prop(self, "interpolation_threshold")
            col.prop(self, "general_optimization_threshold")

        return body


class NodeAnimExportOperator(AnimationExportOperator):

    show_bone_localspace = True

    bone_localspace: BoolProperty(
        name="Bone Localspace",
        description=(
            "When exporting the animation,"
            " ignore the armature object position"),
        default=True
    )

    force_sort_bones: BoolProperty(
        name="Force sort bones",
        description=(
            "Blender doesnt sort bones by name, although this may be desired"
            " in certain scenarios. This ensure the bones are sorted by name"),
        default=False
    )

    short_rot: BoolProperty(
        name="Use 16 bit rotations",
        description="Whether to use 16 bit BAMS for the rotation keyframes",
        default=False
    )

    ensure_positive_euler_angles: BoolProperty(
        name="Ensure positive euler angles",
        description="Ensure that all exported euler rotation angles are positive.",
        default=True
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

    def get_anim_parameters(self):
        return AnimParameters(
            self.bone_localspace,
            self.rotation_mode,
            self.interpolation_threshold,
            self.quaternion_threshold,
            self.general_optimization_threshold,
            self.quaternion_optimization_threshold,
            self.short_rot,
            self.ensure_positive_euler_angles
        )

    def draw_other(self, layout: UILayout):
        self.draw_panel_rotation(layout)
        self.draw_panel_bones(layout)

    def draw_panel_rotation(self, layout: UILayout):
        header, body = layout.panel(
            "SAIO_export_nodeanim_rotation", default_closed=True)
        header.label(text="Rotation")

        if body:
            body.prop(self, "short_rot")
            body.prop(self, "ensure_positive_euler_angles")

        return body

    def draw_panel_bones(self, layout: UILayout):
        if not self.show_bone_localspace:
            return

        header, body = layout.panel(
            "SAIO_export_nodeanim_bone", default_closed=True)
        header.label(text="Bones")

        if body:
            body.prop(self, "bone_localspace")
            body.prop(self, "force_sort_bones")

        return body

    def draw_panel_advanced(self, layout: UILayout):
        body = super().draw_panel_advanced(layout)

        if body:
            col = body.column(heading = "Rotation Conversion", align = True)
            col.prop(self, "rotation_mode")
            col.prop(self, "quaternion_threshold")
            col.prop(self, "quaternion_optimization_threshold")

        return body
