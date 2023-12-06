import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    StringProperty
)
from .base import SAIOBaseFileSaveOperator
from ...utility.draw import expand_menu
from ...utility.anim_parameters import AnimParameters

class ExportOperator(SAIOBaseFileSaveOperator):
    bl_options = {'PRESET', 'UNDO'}

    def export(self, context: bpy.types.Context): # pylint: disable=unused-argument
        return {'FINISHED'}

    def _execute(self, context):
        from os import path
        if len(self.filepath) == 0 or self.filepath.endswith(path.sep):
            self.filepath += "unnamed" + self.filename_ext

        from ...dotnet import load_dotnet
        load_dotnet()

        return self.export(context)


class ExportModelOperator(ExportOperator):

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
        default=False,
    )

    auto_node_attributes: BoolProperty(
        name="Automatic Node Attributes",
        description=(
            "Automatically determine node attributes for the exported model"
        ),
        default=True
    )

    ensure_positive_euler_angles: BoolProperty(
        name="Ensure positive euler angles",
        description="Ensure that all exported euler rotation angles are positive.",
        default=True
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

    multi_export = False

    def export_models(self, context, objects): # pylint: disable=unused-argument
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
            def check(x: bpy.types.Object): # pylint: disable=unused-argument
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
        objects = ExportModelOperator._collect_objects(self.select_mode, context, self.multi_export)
        return self.export_models(context, objects)


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

    show_advanced: BoolProperty(
        name="Advanced",
        default=False
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
        box = self.layout.box()
        if expand_menu(box, self, "show_advanced"):
            box.prop(self, "interpolation_threshold")
            box.prop(self, "general_optimization_threshold")


class NodeAnimExportOperator(AnimationExportOperator):

    show_bone_localspace = True

    bone_localspace: BoolProperty(
        name="Bone Localspace",
        description=(
            "When exporting the animation,"
            " ignore the armature object position"),
        default=True
    )

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

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        if self.show_bone_localspace:
            layout.prop(self, "bone_localspace")
            layout.prop(self, "force_sort_bones")
        layout.prop(self, "short_rot")
        layout.prop(self, "ensure_positive_euler_angles")
        box = layout.box()
        if expand_menu(box, self, "show_advanced"):
            box.prop(self, "rotation_mode")
            box.prop(self, "interpolation_threshold")
            box.prop(self, "quaternion_threshold")
            box.prop(self, "general_optimization_threshold")
            box.prop(self, "quaternion_optimization_threshold")
