import bpy
from bpy.types import Context

from .base_panel import PropertiesPanel

from ..property_groups.material_properties import SAIO_Material
from ..property_groups.material_mass_edit_properties import (
    SAIO_MaterialMassEdit
)
from ..operators.material_operators import (
    SAIO_OT_Material_UpdateActiveProperties
)

from ...utility.draw import prop_advanced


class SAIO_PT_Material(PropertiesPanel):
    bl_label = "SAIO Material Properties"
    bl_context = "material"

    @staticmethod
    def draw_texture_properties(
            layout: bpy.types.UILayout,
            material: bpy.types.Material,
            material_properties: bpy.types.Material,
            mass_edit_properties: SAIO_MaterialMassEdit = None,
            darken_panels=True):

        header, texture_menu = layout.panel("saio_mat_texture", default_closed=True)
        header.label(text="Texture properties")
        if not texture_menu:
            return

        texture_menu.prop(
            material_properties,
            "use_texture",
        )

        block = texture_menu.column()
        block.active = (
            material_properties.use_texture
            or not darken_panels
        )

        def texture_prop(label, name, qe_name):
            prop_advanced(
                block,
                label,
                material_properties,
                name,
                mass_edit_properties,
                qe_name)

        texture_prop("Texture ID:", "texture_id", "apply_texture_id")

        try:
            texture_node: bpy.types.ShaderNodeTexImage \
                = material.node_tree.nodes["SAIO Texture"]

            block.prop_search(
                texture_node, "image", bpy.data, "images", text='Texture')

        except Exception:
            pass

        texture_prop("Environment Texture:", "use_environment", None)

        block.separator(factor=2)

        texture_prop("Texture Filtering:", "texture_filtering", "apply_filter")
        texture_prop("Anisotropic filtering:", "anisotropic_filtering", None)
        texture_prop("Mipmap distance multiplier:",
                     "mipmap_distance_multiplier",
                     "apply_mipmap_distance_multiplier")

        block.separator(factor=2)

        # === UV ===
        grid = block.grid_flow(columns=2, even_columns=True)

        grid.label(text="UV Sampler")
        grid.label(text="Clamp")
        grid.label(text="Mirror")

        grid.label(text="U     V")

        clamp_row = grid.row()
        clamp_row.prop(material_properties, "clamp_u", text="")
        clamp_row.prop(material_properties, "clamp_v", text="")

        mirror_row = grid.row()
        mirror_row.prop(material_properties, "mirror_u", text="")
        mirror_row.prop(material_properties, "mirror_v", text="")

    @staticmethod
    def draw_rendering_properties(
            layout: bpy.types.UILayout,
            material_properties: SAIO_Material,
            mass_edit_properties: SAIO_MaterialMassEdit = None,
            darken_panels=True):

        header, rendering_menu = layout.panel("saio_mat_rendering", default_closed=True)
        header.label(text="Rendering properties")
        if not rendering_menu:
            return

        def rendering_prop(label, name):
            prop_advanced(
                rendering_menu,
                label,
                material_properties,
                name)

        rendering_prop("Use Alpha:", "use_alpha")
        alpha_column = rendering_menu.column()
        alpha_column.active = (
            material_properties.use_alpha
            or not darken_panels
        )

        prop_advanced(
            alpha_column,
            "Source Alpha:",
            material_properties,
            "source_alpha",
            mass_edit_properties,
            "apply_source_alpha")

        prop_advanced(
            alpha_column,
            "Destination Alpha:",
            material_properties,
            "destination_alpha",
            mass_edit_properties,
            "apply_destination_alpha")

        prop_advanced(
            alpha_column,
            "No Alpha Test:",
            material_properties,
            "no_alpha_test",
            mass_edit_properties,
            "apply_no_alpha_test")

        rendering_menu.separator(factor=2)

        rendering_prop("Double Sided:", "double_sided")
        rendering_prop("Ignore Lighting:", "ignore_diffuse")
        rendering_prop("Ignore Ambient Lighting:", "ignore_ambient")
        rendering_prop("Ignore Specular Lighting:", "ignore_specular")
        rendering_prop("Flat Shading:", "flat_shading")

    @staticmethod
    def draw_gc_properties(
            layout: bpy.types.UILayout,
            material_properties: SAIO_Material,
            quick_edit_properties: SAIO_MaterialMassEdit = None):

        header, gc_menu = layout.panel("saio_mat_gc", default_closed=True)
        header.label(text="SA2B specific")
        if not gc_menu:
            return

        def gc_prop(label, name, qe_name):
            prop_advanced(
                gc_menu,
                label,
                material_properties,
                name,
                quick_edit_properties,
                qe_name)

        gc_prop("Shadow Stencil:", "shadow_stencil", "apply_shadow_stencil")

        gc_prop("Texgen coord output slot:",
                "texgen_coord_id", "apply_texgen_coord_id")

        gc_prop("Texgen type", "texgen_type", "apply_texgen_type")

        gc_prop("Texgen Matrix ID:", "texgen_matrix_id",
                "apply_texgen_matrix_id")

        gc_prop("Texgen Source:", "texgen_source",
                "apply_texgen_source")

    @staticmethod
    def draw_material_properties(
            layout: bpy.types.UILayout,
            material: bpy.types.Material,
            material_properties: bpy.types.Material,
            mass_edit_properties: SAIO_MaterialMassEdit = None,
            darken_panels=True,
            show_operator=True):

        if show_operator:
            layout.operator(SAIO_OT_Material_UpdateActiveProperties.bl_idname)

        def color_prop(label, name, qe_name):
            prop_advanced(
                layout,
                label,
                material_properties,
                name,
                mass_edit_properties,
                qe_name)

        color_prop("Diffuse Color:", "diffuse", "apply_diffuse")
        color_prop("Specular Color:", "specular", "apply_specular")
        color_prop("Ambient Color:", "ambient", "apply_ambient")
        color_prop("Specular Strength:",
                   "specular_exponent", "apply_specularity")

        SAIO_PT_Material.draw_texture_properties(
            layout,
            material,
            material_properties,
            mass_edit_properties,
            darken_panels)

        SAIO_PT_Material.draw_rendering_properties(
            layout,
            material_properties,
            mass_edit_properties,
            darken_panels)

        SAIO_PT_Material.draw_gc_properties(
            layout,
            material_properties,
            mass_edit_properties)

    # === overriden methods === #

    @classmethod
    def poll(cls, context: Context):
        return cls.verify(context) is None

    @classmethod
    def verify(cls, context: bpy.types.Context):
        obj = context.active_object
        if obj is None:
            return "No active object"

        if obj.type != 'MESH':
            return "Active object not a mesh"

        if obj.active_material is None:
            return "No active material"

        return None

    def draw_panel(self, context):

        SAIO_PT_Material.draw_material_properties(
            self.layout,
            context.active_object.active_material,
            context.active_object.active_material.saio_material)
