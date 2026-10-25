import bpy

from .base_panel import PropertiesPanel

from ..property_groups.material_properties import SAIO_Material
from ..property_groups.ginja_material_properties import SAIO_Material_Ginja
from ..property_groups.mesh_properties import MESH_DATA_TYPES

from ...utility.draw import col_prop


class SAIO_PT_Material(PropertiesPanel):
    bl_label = "SAIO Material Properties"
    bl_context = "material"

    @staticmethod
    def draw_ginja_tevstg_properties(
        layout: bpy.types.UILayout,
        ginja_material: SAIO_Material_Ginja):

        header, menu = layout.panel("saio_mat_ginja_tevstg")
        header.label(text="Ginja Tev-stage")
        if not menu:
            return

        menu.use_property_decorate = False
        menu.use_property_split = True

        col_prop(menu, ginja_material, "tevstg_manual", text="Manual")

        parameters_layout = menu.column()
        parameters_layout.active = ginja_material.tevstg_manual

        parameters_layout.prop(ginja_material, "tevstg_stage", text="Stage")
        parameters_layout.prop(ginja_material, "tevstg_tex_coord", text="Texture coordiantes")
        parameters_layout.prop(ginja_material, "tevstg_tex_map", text="Texture map")
        parameters_layout.prop(ginja_material, "tevstg_color_channel", text="Color channel")


    @staticmethod
    def draw_ginja_texgen_properties(
        layout: bpy.types.UILayout,
        ginja_material: SAIO_Material_Ginja):

        header, menu = layout.panel("saio_mat_ginja_texgen")
        header.label(text="Ginja Tex-gen")
        if not menu:
            return

        menu.use_property_decorate = False
        menu.use_property_split = True

        col_prop(menu, ginja_material, "texgen_manual", text="Manual")

        parameters_layout = menu.column()
        parameters_layout.active = ginja_material.texgen_manual

        parameters_layout.prop(ginja_material, "texgen_tex_coord", text="Texture coordinates")
        parameters_layout.prop(ginja_material, "texgen_type", text="Type")
        parameters_layout.prop(ginja_material, "texgen_source", text="Source")
        parameters_layout.prop(ginja_material, "texgen_matrix_id", text="Matrix")


    @staticmethod
    def draw_rendering_properties(
        layout: bpy.types.UILayout,
        file_format: str,
        saio_material: SAIO_Material):

        header, menu = layout.panel("saio_mat_rendering")
        header.label(text="Rendering")
        if not menu:
            return

        menu.use_property_decorate = False
        menu.use_property_split = True

        if file_format in ['CHUNK', 'BASIC']:
            menu.prop(saio_material, "rendering_model")

        menu.column(heading="Double sided").prop(saio_material, "double_sided", text="")

        if file_format == 'GINJA':

            col_prop(menu, saio_material.ginja_properties, "vertex_color_for_diffuse")
            col_prop(menu, saio_material.ginja_properties, "vertex_color_for_ambient")

            SAIO_PT_Material.draw_ginja_tevstg_properties(menu, saio_material.ginja_properties)


    @staticmethod
    def draw_transparency_properties(
        layout: bpy.types.UILayout,
        saio_material: SAIO_Material):

        header, menu = layout.panel("saio_mat_transparency")
        header.label(text="Transparency")
        if not menu:
            return

        menu.use_property_decorate = False
        menu.use_property_split = True

        menu.prop(saio_material, "alpha_mode")

        blendmode_layout = menu.column()
        blendmode_layout.active = saio_material.alpha_mode != 'OPAQUE'

        blendmode_layout.prop(saio_material, "source_blendmode")
        blendmode_layout.prop(saio_material, "destination_blendmode")


    @staticmethod
    def draw_lighting_properties(
        layout: bpy.types.UILayout,
        file_format: str,
        saio_material: SAIO_Material):

        header, menu = layout.panel("saio_mat_lighting")
        header.label(text="Lighting")
        if not menu:
            return

        menu.use_property_decorate = False
        menu.use_property_split = True

        col_prop(menu, saio_material, "ignore_lighting")

        if file_format in ["CHUNK", "GINJA"]:
            col_prop(menu, saio_material, "ignore_ambient")

        col_prop(menu, saio_material, "ignore_specular")


    @staticmethod
    def draw_color_properties(
        layout: bpy.types.UILayout,
        file_format: str,
        saio_material: SAIO_Material):

        header, menu = layout.panel("saio_mat_colors")
        header.label(text="Colors")
        if not menu:
            return

        menu.use_property_decorate = False
        menu.use_property_split = True

        menu.prop(saio_material, "diffuse")

        if file_format in ["CHUNK", "GINJA"]:
            ambient_layout = menu.column()
            ambient_layout.active = not saio_material.ignore_lighting and not saio_material.ignore_ambient
            ambient_layout.prop(saio_material, "ambient")

        specular_layout = menu.column()
        specular_layout.active = not saio_material.ignore_specular
        specular_layout.prop(saio_material, "specular")
        specular_layout.prop(saio_material, "specular_exponent")


    @staticmethod
    def draw_texture_properties(
        layout: bpy.types.UILayout,
        file_format: str,
        saio_material: SAIO_Material):

        header, menu = layout.panel("saio_mat_texture")
        header.label(text="Texture")
        if not menu:
            return

        menu.use_property_decorate = False
        menu.use_property_split = True

        col_prop(menu, saio_material, "use_texture")
        
        menu = menu.column()
        menu.active = saio_material.use_texture

        menu.prop(saio_material, "texture_id")
        if file_format == 'GINJA':
            menu.prop(saio_material.ginja_properties, "texture_slot")

        if file_format in ["CHUNK", "BASIC"]:
            menu.separator(type="LINE")
            menu.prop(saio_material, "texture_filtering")
            col_prop(menu, saio_material, "anisotropic_filtering")
            menu.prop(saio_material, "mipmap_distance_multiplier")

        menu.separator(type="LINE")
        menu.prop(saio_material, "texturing_mode")

        env_layout = menu.column()
        env_layout.active = saio_material.texturing_mode=='ENV'
        col_prop(env_layout, saio_material, "env_include_uvs")

        uv_layout = menu.column()
        uv_layout.active = saio_material.texturing_mode=='UV' or saio_material.env_include_uvs

        if file_format == 'GINJA':
            uv_layout.prop(saio_material, "uv_precision_level")
        elif file_format == 'CHUNK':
            uv_layout.prop(saio_material, "uv_range")

        menu.separator(type="LINE")
        split = menu.split(factor=0.4)
        split.use_property_split = False
        
        labels = split.column()
        labels.alignment = 'RIGHT'
        labels.label(text="Texture Sampling")
        labels.label(text="Clamp")
        labels.label(text="Mirror")

        row = split.row()
        row.alignment = 'LEFT'
        
        horizontal = row.column()
        horizontal.alignment = 'LEFT'
        horizontal.label(text="U")
        horizontal.prop(saio_material, "clamp_u", text="")
        horizontal.prop(saio_material, "mirror_u", text="")

        vertical = row.column()
        vertical.alignment = 'LEFT'
        vertical.label(text="V")
        vertical.prop(saio_material, "clamp_v", text="")
        vertical.prop(saio_material, "mirror_v", text="")

        if file_format == 'GINJA':
            SAIO_PT_Material.draw_ginja_texgen_properties(menu, saio_material.ginja_properties)


    @staticmethod
    def draw_material_properties(
            layout: bpy.types.UILayout,
            file_format: str,
            material: bpy.types.Material | None,
            saio_material: bpy.types.Material):

        SAIO_PT_Material.draw_rendering_properties(layout, file_format, saio_material)
        SAIO_PT_Material.draw_transparency_properties(layout, saio_material)
        SAIO_PT_Material.draw_lighting_properties(layout, file_format, saio_material)
        SAIO_PT_Material.draw_color_properties(layout, file_format, saio_material)
        SAIO_PT_Material.draw_texture_properties(layout, file_format, saio_material)


    # === overriden methods === #

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return cls.verify(context) is None

    @classmethod
    def verify(cls, context: bpy.types.Context):
        obj = context.active_object
        if obj is None:
            return "No active object"

        if obj.type not in MESH_DATA_TYPES:
            return "Active object not a mesh"

        if obj.active_material is None:
            return "No active material"

        return None

    def draw_panel(self, context):
        SAIO_PT_Material.draw_material_properties(
            self.layout,
            context.scene.saio_scene.file_format,
            context.active_object.active_material,
            context.active_object.active_material.saio_material)