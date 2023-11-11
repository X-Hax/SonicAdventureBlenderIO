import bpy
from bpy.props import (
    EnumProperty,
)
from bpy.types import Context

from .base import SAIOBaseOperator

from ..property_groups.material_mass_edit_properties import (
    SAIO_MaterialMassEdit
)

PROPERTY_MAPPING: list[tuple[str | None, str]] = {
    ("apply_diffuse", "diffuse"),
    ("apply_specular", "specular"),
    ("apply_ambient", "ambient"),
    ("apply_specularity", "specular_exponent"),

    (None, "use_texture"),
    ("apply_texture_id", "texture_id"),
    (None, "use_environment"),
    ("apply_filter", "texture_filtering"),
    (None, "anisotropic_filtering"),
    ("apply_mipmap_distance_multiplier", "mipmap_distance_multiplier"),
    (None, "clamp_u"),
    (None, "clamp_v"),
    (None, "mirror_u"),
    (None, "mirror_v"),

    (None, "use_alpha"),
    ("apply_source_alpha", "source_alpha"),
    ("apply_destination_alpha", "destination_alpha"),
    (None, "double_sided"),
    (None, "ignore_ambient"),
    (None, "ignore_diffuse"),
    (None, "ignore_specular"),
    (None, "flat_shading"),

    ("apply_shadow_stencil", "shadow_stencil"),
    ("apply_texgen_coord_id", "texgen_coord_id"),
    ("apply_texgen_type", "texgen_type"),
    ("apply_texgen_matrix_id", "texgen_matrix_id"),
    ("apply_texgen_source", "texgen_source"),
}


class SAIO_OT_MaterialMassEdit_Set(SAIOBaseOperator):
    bl_idname = "saio.matmassedit_set"
    bl_label = "Set Props"
    bl_description = "Sets checked items in enabled Quick Edit Menu"
    bl_options = {'UNDO'}

    mode: EnumProperty(
        name="Mode",
        items=(
            ('ALL', "all", "all"),
            ('ADD', "add", "add"),
            ('REMOVE', "remove", "remove"),
        )
    )

    @staticmethod
    def get_materials(context: bpy.types.Context):

        if context.mode != 'OBJECT':
            return []

        result = []
        for obj in context.selected_objects:
            if obj.type != 'MESH':
                continue
            for material_slot in obj.material_slots:
                mat = material_slot.material
                if mat is not None and mat not in result:
                    result.append(mat)

        return [mat.saio_material for mat in result]

    @classmethod
    def poll(cls, context: Context):
        return context.mode == 'OBJECT'

    def _execute(self, context):

        mass_edit_properties: SAIO_MaterialMassEdit \
            = context.scene.saio_scene.material_mass_edit

        targets = SAIO_OT_MaterialMassEdit_Set.get_materials(context)

        if self.mode == 'ADD':
            def set_prop(properties, apply_name, name):
                if apply_name is not None:
                    confirm = getattr(mass_edit_properties, apply_name)
                    if not confirm:
                        return

                    value = getattr(properties, name)
                    for target in targets:
                        setattr(target, name, value)

                elif getattr(properties, name):
                    for target in targets:
                        setattr(target, name, True)

        elif self.mode == 'REMOVE':
            def set_prop(properties, apply_name, name):
                if apply_name is None and getattr(properties, name):
                    for target in targets:
                        setattr(target, name, False)

        else:  # All
            def set_prop(properties, apply_name, name):
                value = getattr(properties, name)
                for target in targets:
                    setattr(target, name, value)

        for m in PROPERTY_MAPPING:
            set_prop(mass_edit_properties.material_properties, m[0], m[1])

        return {'FINISHED'}


class SAIO_OT_MaterialMassEdit_Reset(SAIOBaseOperator):
    bl_idname = "saio.matmassedit_reset"
    bl_label = "Reset Parameters"
    bl_description = "Resets the material mass edit parameters"
    bl_options = {'UNDO'}

    def _execute(self, context: Context):
        from ...utility.general import reset_property_group

        mass_edit_properties: SAIO_MaterialMassEdit \
            = context.scene.saio_scene.material_mass_edit

        reset_property_group(mass_edit_properties, True)
        reset_property_group(mass_edit_properties.material_properties, True)

        return {'FINISHED'}
