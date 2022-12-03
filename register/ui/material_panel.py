import bpy

from ..property_groups import (
    material_properties as saio_material,
    panel_properties,
    quick_edit_properties
)

from .draw import (
    prop_advanced,
    expand_menu
)


class SAIO_PT_Material(bpy.types.Panel):
    bl_label = "SAIO Material Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_options = {"DEFAULT_CLOSED"}

    @staticmethod
    def draw_texture_properties(
            layout: bpy.types.UILayout,
            material: bpy.types.Material,
            material_properties: bpy.types.Material,
            panel_settings: panel_properties.SAIO_PanelSettings,
            quick_edit_properties: quick_edit_properties.SAIO_QuickEdit = None,
            darken_panels=True):

        texture_menu = layout.box()
        if not expand_menu(
                texture_menu,
                panel_settings,
                "expanded_texture_properties"):
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
                quick_edit_properties,
                qe_name)

        texture_prop("Texture ID:", "texture_id", "apply_texture_id")
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
            material_properties: saio_material.SAIO_Material,
            panel_settings: panel_properties.SAIO_PanelSettings,
            quick_edit_properties: quick_edit_properties.SAIO_QuickEdit = None,
            darken_panels=True):

        rendering_menu = layout.box()
        if not expand_menu(
                rendering_menu,
                panel_settings,
                "expanded_rendering_properties"):
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
            quick_edit_properties,
            "apply_source_alpha")

        prop_advanced(
            alpha_column,
            "Destination Alpha:",
            material_properties,
            "destination_alpha",
            quick_edit_properties,
            "apply_destination_alpha")

        rendering_menu.separator(factor=2)

        rendering_prop("Enable Culling:", "culling")
        rendering_prop("Ignore Ambient Lighting:", "ignore_ambient")
        rendering_prop("Ignore Diffuse Lighting:", "ignore_diffuse")
        rendering_prop("Ignore Specular Lighting:", "ignore_specular")
        rendering_prop("Flat Shading:", "flat_shading")

    @staticmethod
    def draw_gc_properties(
            layout: bpy.types.UILayout,
            material_properties: saio_material.SAIO_Material,
            panel_settings: panel_properties.SAIO_PanelSettings,
            quick_edit_properties: quick_edit_properties.SAIO_QuickEdit = None):

        gc_menu = layout.box()
        if not expand_menu(
                gc_menu,
                panel_settings,
                "expanded_gc_properties"):
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

        if material_properties.texgen_type[0] == 'M':
            gc_prop("Texgen Matrix ID:", "texgen_matrix_id",
                    "apply_texgen_matrix_id")

            gc_prop("Texgen Source:", "texgen_source_matrix",
                    "apply_texgen_source")

        elif material_properties.texgen_type[0] == 'B':
            gc_prop("Texgen Source:", "texgen_source_bitmap",
                    "apply_texgen_source")
        else:
            gc_prop("Texgen Source:", "texgen_source_srtg",
                    "apply_texgen_source")

    @staticmethod
    def draw_panel(
            layout: bpy.types.UILayout,
            material: bpy.types.Material,
            material_properties: bpy.types.Material,
            panel_settings: panel_properties.SAIO_PanelSettings,
            quick_edit_properties: quick_edit_properties.SAIO_QuickEdit = None,
            darken_panels=True):

        def color_prop(label, name, qe_name):
            prop_advanced(
                layout,
                label,
                material_properties,
                name,
                quick_edit_properties,
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
            panel_settings,
            quick_edit_properties,
            darken_panels)

        SAIO_PT_Material.draw_rendering_properties(
            layout,
            material_properties,
            panel_settings,
            quick_edit_properties,
            darken_panels)

        SAIO_PT_Material.draw_gc_properties(
            layout,
            material_properties,
            panel_settings,
            quick_edit_properties)

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return (
            context.active_object is not None
            and context.active_object.type == 'MESH'
            and context.active_object.active_material is not None
        )

    def draw(self, context):
        SAIO_PT_Material.draw_panel(
            self.layout,
            context.active_object.active_material,
            context.active_object.active_material.saio_material,
            context.scene.saio_settings.panels)
