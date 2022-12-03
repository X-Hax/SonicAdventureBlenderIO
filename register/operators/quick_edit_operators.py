import os
import bpy
from bpy.types import Operator
from bpy.props import (
    EnumProperty,
)

from ..property_groups import quick_edit_properties

PROPERTY_MAPPING = {
    "material": [
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
        (None, "culling"),
        (None, "ignore_ambient"),
        (None, "ignore_diffuse"),
        (None, "ignore_specular"),
        (None, "flat_shading"),

        ("apply_shadow_stencil", "shadow_stencil"),
        ("apply_texgen_coord_id", "texgen_coord_id"),
        ("apply_texgen_type", "texgen_type"),
    ],
    "material_M": [
        ("apply_texgen_matrix_id", "texgen_matrix_id"),
        ("apply_texgen_source", "texgen_source_matrix"),
    ],
    "material_B": [
        ("apply_texgen_source", "texgen_source_bitmap"),
    ],
    "material_S": [
        ("apply_texgen_source", "texgen_source_srtg"),
    ],
    "land_entry": [
        ("apply_blockbit", "blockbit")
    ],
    "land_entry_UNIVERSAL": [
        (None, "sf_visible"),
        (None, "sf_solid"),
        (None, "sf_water"),
        (None, "sf_water_no_alpha"),
        (None, "sf_accelerate"),
        (None, "sf_low_acceleration"),
        (None, "sf_no_acceleration"),
        (None, "sf_increased_acceleration"),
        (None, "sf_tube_acceleration"),
        (None, "sf_no_friction"),
        (None, "sf_cannot_land"),
        (None, "sf_unclimbable"),
        (None, "sf_stairs"),
        (None, "sf_diggable"),
        (None, "sf_hurt"),
        (None, "sf_dynamic_collision"),
        (None, "sf_water_collision"),
        (None, "sf_gravity"),
        (None, "sf_footprints"),
        (None, "sf_no_shadows"),
        (None, "sf_no_fog"),
        (None, "sf_low_depth"),
        (None, "sf_use_sky_draw_distance"),
        (None, "sf_easy_draw"),
        (None, "sf_no_zwrite"),
        (None, "sf_draw_by_nesh"),
        (None, "sf_enable_manipulation"),
        (None, "sf_waterfall"),
        (None, "sf_chaos0_land"),
        (None, "sf_transform_bounds"),
        (None, "sf_bounds_radius_small"),
        (None, "sf_bounds_radius_tiny"),
        (None, "sf_sa1_unknown9"),
        (None, "sf_sa1_unknown11"),
        (None, "sf_sa1_unknown15"),
        (None, "sf_sa1_unknown19"),
        (None, "sf_sa2_unknown6"),
        (None, "sf_sa2_unknown9"),
        (None, "sf_sa2_unknown14"),
        (None, "sf_sa2_unknown16"),
        (None, "sf_sa2_unknown17"),
        (None, "sf_sa2_unknown18"),
        (None, "sf_sa2_unknown25"),
        (None, "sf_sa2_unknown26"),
    ],
    "land_entry_SA1": [
        (None, "sf_solid"),
        (None, "sf_water"),
        (None, "sf_no_friction"),
        (None, "sf_no_acceleration"),
        (None, "sf_low_acceleration"),
        (None, "sf_use_sky_draw_distance"),
        (None, "sf_cannot_land"),
        (None, "sf_increased_acceleration"),
        (None, "sf_diggable"),
        (None, "sf_sa1_unknown9"),
        (None, "sf_waterfall"),
        (None, "sf_sa1_unknown11"),
        (None, "sf_unclimbable"),
        (None, "sf_chaos0_land"),
        (None, "sf_stairs"),
        (None, "sf_sa1_unknown15"),
        (None, "sf_hurt"),
        (None, "sf_tube_acceleration"),
        (None, "sf_low_depth"),
        (None, "sf_sa1_unknown19"),
        (None, "sf_footprints"),
        (None, "sf_accelerate"),
        (None, "sf_water_collision"),
        (None, "sf_gravity"),
        (None, "sf_no_zwrite"),
        (None, "sf_draw_by_nesh"),
        (None, "sf_enable_manipulation"),
        (None, "sf_dynamic_collision"),
        (None, "sf_transform_bounds"),
        (None, "sf_bounds_radius_small"),
        (None, "sf_bounds_radius_tiny"),
        (None, "sf_visible"),
    ],
    "land_entry_SA2": [
        (None, "sf_solid"),
        (None, "sf_water"),
        (None, "sf_no_friction"),
        (None, "sf_no_acceleration"),
        (None, "sf_low_acceleration"),
        (None, "sf_diggable"),
        (None, "sf_sa2_unknown6"),
        (None, "sf_unclimbable"),
        (None, "sf_stairs"),
        (None, "sf_sa2_unknown9"),
        (None, "sf_hurt"),
        (None, "sf_footprints"),
        (None, "sf_cannot_land"),
        (None, "sf_water_no_alpha"),
        (None, "sf_sa2_unknown14"),
        (None, "sf_no_shadows"),
        (None, "sf_sa2_unknown16"),
        (None, "sf_sa2_unknown17"),
        (None, "sf_sa2_unknown18"),
        (None, "sf_gravity"),
        (None, "sf_tube_acceleration"),
        (None, "sf_increased_acceleration"),
        (None, "sf_no_fog"),
        (None, "sf_use_sky_draw_distance"),
        (None, "sf_easy_draw"),
        (None, "sf_sa2_unknown25"),
        (None, "sf_sa2_unknown26"),
        (None, "sf_dynamic_collision"),
        (None, "sf_transform_bounds"),
        (None, "sf_bounds_radius_small"),
        (None, "sf_bounds_radius_tiny"),
        (None, "sf_visible"),
    ],
    "node": [
        (None, "ignore_position"),
        (None, "ignore_rotation"),
        (None, "ignore_scale"),
        (None, "rotate_zyx"),
        (None, "skip_draw"),
        (None, "skip_children"),
        (None, "no_animate"),
        (None, "no_morph"),
    ],
    "mesh": [
        (None, "force_vertex_colors")
    ],
}


def map_quick_edit_properties(
        quick_edit_properties: quick_edit_properties.SAIO_QuickEdit):

    result = {}

    if quick_edit_properties.use_material_edit:
        mode = quick_edit_properties.material_properties.texgen_type[0]

        mapping = []
        mapping.extend(PROPERTY_MAPPING["material"])
        mapping.extend(PROPERTY_MAPPING[f"material_{mode}"])

        result[quick_edit_properties.material_properties] = mapping

    if quick_edit_properties.use_land_entry_edit:
        mode = quick_edit_properties.panels \
            .land_entry_surface_attributes_editmode

        mapping = []
        mapping.extend(PROPERTY_MAPPING["land_entry"])
        mapping.extend(PROPERTY_MAPPING[f"land_entry_{mode}"])

        result[quick_edit_properties.land_entry_properties] = mapping

    if quick_edit_properties.use_node_edit:
        result[quick_edit_properties.node_properties] \
            = PROPERTY_MAPPING["node"]

    if quick_edit_properties.use_mesh_edit:
        result[quick_edit_properties.mesh_properties] \
            = PROPERTY_MAPPING["mesh"]

    return result


class SAIO_OT_QuickEdit_Set(Operator):
    bl_idname = "saio.quickedit_set"
    bl_label = "Set Props"
    bl_description = "Sets checked items in enabled Quick Edit Menu"

    mode: EnumProperty(
        name="Mode",
        items=(
            ('ALL', "all", "all"),
            ('ADD', "add", "add"),
            ('REMOVE', "remove", "remove"),
        )
    )

    @staticmethod
    def get_nodes(context: bpy.types.Context):

        result = []

        if context.mode == 'OBJECT':
            for obj in context.selected_objects:
                if (obj.type not in ['MESH', 'ARMATURE', 'EMPTY']
                        or obj in result):
                    continue
                result.append(obj)

        elif context.mode == 'POSE':
            result = [bone for bone in context.active_object.data.bones]
        elif context.mode == 'EDIT_ARMATURE':
            result = [bone for bone in context.active_object.data.edit_bones]

        return [node.saio_node for node in result]

    @staticmethod
    def get_land_entries(context: bpy.types.Context):

        if context.mode != 'OBJECT':
            return []

        result = []
        for obj in context.selected_objects:
            if obj.type != 'MESH' or obj in result:
                continue
            result.append(obj)

        return [obj.saio_land_entry for obj in result]

    @staticmethod
    def get_meshes(context: bpy.types.Context):

        if context.mode != 'OBJECT':
            return []

        result = []
        for obj in context.selected_objects:
            if obj.type != 'MESH' or obj.data in result:
                continue
            result.append(obj.data)

        return [mesh.saio_mesh for mesh in result]

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

    def execute(self, context):

        quick_edit_properties: quick_edit_properties.SAIO_QuickEdit \
            = context.scene.saio_settings.quick_edit

        prop_mapping = map_quick_edit_properties(quick_edit_properties)
        targets = []

        if self.mode == 'ADD':
            def set_prop(properties, apply_name, name):
                if apply_name is not None:
                    confirm = getattr(quick_edit_properties, apply_name)
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

        for props, mapping in prop_mapping.items():

            if props == quick_edit_properties.node_properties:
                targets = SAIO_OT_QuickEdit_Set.get_nodes(
                    context)

            elif props == quick_edit_properties.land_entry_properties:
                targets = SAIO_OT_QuickEdit_Set.get_land_entries(
                    context)

            elif props == quick_edit_properties.mesh_properties:
                targets = SAIO_OT_QuickEdit_Set.get_meshes(
                    context)

            elif props == quick_edit_properties.material_properties:
                targets = SAIO_OT_QuickEdit_Set.get_materials(
                    context)

            else:
                raise Exception("Invalid property mapping")

            for m in mapping:
                set_prop(props, m[0], m[1])

        return {'FINISHED'}


class SAIO_OT_QuickEdit_Select(Operator):
    bl_idname = "saio.quickedit_select"
    bl_label = "Quick Edit Selection"
    bl_description = "Selects quick edit settings"

    mode: EnumProperty(
        name="Mode",
        items=(
            ('ADD', "add", "add"),
            ('REMOVE', "remove", "remove"),
            ('INVERT', "invert", "invert"),
        )
    )

    def execute(self, context):

        quick_edit_properties = context.scene.saio_settings.quick_edit
        prop_mapping = map_quick_edit_properties(quick_edit_properties)

        if self.mode == 'ADD':
            def set_prop(properties, apply_name, name):
                if apply_name is None:
                    setattr(properties, name, True)
                else:
                    setattr(quick_edit_properties, apply_name, True)

        elif self.mode == 'REMOVE':
            def set_prop(properties, apply_name, name):
                if apply_name is None:
                    setattr(properties, name, False)
                else:
                    setattr(quick_edit_properties, apply_name, False)

        else:
            def set_prop(properties, apply_name, name):
                if apply_name is None:
                    previous = getattr(properties, name)
                    setattr(properties, name, not previous)
                else:
                    previous = getattr(quick_edit_properties, apply_name)
                    setattr(quick_edit_properties, apply_name, not previous)

        for props, mapping in prop_mapping.items():
            for m in mapping:
                set_prop(props, m[0], m[1])

        return {'FINISHED'}
