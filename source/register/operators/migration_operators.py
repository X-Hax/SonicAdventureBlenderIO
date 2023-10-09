import bpy
from bpy.types import Context, Event
from bpy.props import BoolProperty
from mathutils import Matrix, Vector

from .base import SAIOBaseOperator, SAIOBasePopupOperator

from ...migration import ARMATURE_KEY
from ...utility.math_utils import get_normal_matrix
from ...exceptions import UserException


class SAIO_OT_MigrateCheck(SAIOBaseOperator):
    bl_idname = "saio.migrate_check"
    bl_label = "Check for migrate data"
    bl_description = "Check wether there is data to migrate from the old addon"

    @classmethod
    def poll(cls, context: Context):
        return context.mode == 'OBJECT'

    def _execute(self, context: bpy.types.Context):
        from ...migration import migration_checks
        migration_checks.update_checks()
        return {'FINISHED'}


class SAIO_OT_MigrateData(SAIOBasePopupOperator):
    bl_idname = "saio.migrate_data"
    bl_label = "Migrate Data"
    bl_description = "Migrate data from the old addon to the new one"
    bl_options = {'PRESET', 'UNDO'}

    remigrate: BoolProperty(
        name="Remigrate",
        description="Migrate previously migrated data again",
        default=False
    )

    @classmethod
    def poll(cls, context: Context):
        return context.mode == 'OBJECT'

    def draw(self, context: Context):
        self.layout.prop(self, "remigrate")

        if self.remigrate:
            self.layout.label(text="!!WARNING!!")
            self.layout.label(
                text="Remigrating will overwrite data that"
                " was in place before migration!")
            self.layout.label(text="Only proceed only if 100% sure!!")

    def _execute(self, context: bpy.types.Context):
        from ... import migration
        migration.migrate_file(self.remigrate)
        return {'FINISHED'}


class SAIO_OT_MigrateArmature(SAIOBasePopupOperator):
    bl_idname = "saio.migrate_armature"
    bl_label = "Migrate Armature"
    bl_description = (
        "Armatures in the old addon interpreted the Armature object itself as"
        " the root. The new addon adds a literal root bone to allow for"
        " animating it proper")
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context: Context):
        return (
            context.mode == 'OBJECT'
            and context.active_object is not None
            and context.active_object.type == 'ARMATURE'
            and 'saObjflags' in context.active_object)

    def draw(self, context: Context):
        self.layout.label(text="!! WARNING !!")
        self.layout.label(
            text="The armature seems to have already been migrated.")
        self.layout.label(
            text="If you migrate again, another bone will be added.")

    def _invoke(self, context: Context, event: Event):
        if ARMATURE_KEY in context.active_object.data:
            return super()._invoke(context, event)
        return self._execute(context)

    def _execute(self, context: Context):

        armature_object = context.active_object
        armature: bpy.types.Armature = armature_object.data

        matrix = armature_object.matrix_local.copy()
        armature_object.matrix_local = Matrix.Identity(4)

        for child in armature_object.children:
            child: bpy.types.Object
            child.matrix_parent_inverse = matrix @ child.matrix_parent_inverse

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        parentless = []
        for edit_bone in armature.edit_bones:
            edit_bone.matrix = matrix @ edit_bone.matrix
            if edit_bone.parent is None:
                parentless.append(edit_bone)

        root_bone = armature.edit_bones.new(armature_object.name)
        root_bone.head = (0, 0, 0)
        root_bone.tail = (1, 0, 0)
        root_bone.matrix = matrix
        for bone in parentless:
            bone.parent = root_bone

        bpy.ops.object.mode_set(mode='OBJECT')

        armature_object.data[ARMATURE_KEY] = True
        return {'FINISHED'}


class SAIO_OT_MigratePath(SAIOBaseOperator):
    bl_idname = "saio.migrate_path"
    bl_label = "Migrate Path"
    bl_description = "Converts an old path to a new one"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context: Context):
        return (
            context.mode == 'OBJECT'
            and context.active_object is not None
            and context.active_object.type == 'CURVE'
            and len(context.active_object) > 0)

    def _execute(self, context: Context):

        curve_object = context.active_object
        curve: bpy.types.Curve = curve_object.data

        if len(curve.splines) == 0:
            raise UserException("Selected curve has no splines!")
        elif len(curve.splines) > 1:
            raise UserException("Curve has more than 1 splines!")

        spline = curve.splines[0]
        if spline.type == 'BEZIER':
            raise UserException(
                "Spline in curve is not a valid type! Must be poly or nurbs")

        positions = []
        for point in spline.points:
            positions.append(point.co.to_3d())

        normals = [Vector((0, 0, 1))] * len(positions)
        children: list[bpy.types.Object] = []
        for child in curve_object.children:
            if child.parent_type != 'VERTEX':
                continue

            matrix = get_normal_matrix(child.matrix_world)
            index = child.parent_vertices[0]
            normals[index] = matrix @ Vector((0, 0, 1))
            children.append(child)

        curve.splines.remove(spline)

        from ...exporting.o_path import DEFAULT_CURVE_CONFIG
        for name, value in DEFAULT_CURVE_CONFIG.items():
            setattr(curve, name, value)
        curve.resolution_u = 1

        from ...importing.i_path import PathProcessor
        processor = PathProcessor()
        bezier_spline = curve.splines.new('BEZIER')
        processor.process_spline(
            positions, normals, curve_object, bezier_spline)

        for child in children:
            bpy.data.objects.remove(child)

        curve.extrude = 1

        return {'FINISHED'}
