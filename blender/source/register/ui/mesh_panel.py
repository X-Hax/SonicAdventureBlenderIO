import bpy
from .base_panel import PropertiesPanel
from ..property_groups.mesh_properties import SAIO_Mesh, WEIGHTED_VERTEX_CHUNKS, USER_ATTRIBUTE_VERTEX_CHUNKS
from ...utility.draw import col_prop


class SAIO_PT_Mesh(PropertiesPanel):
    bl_label = "SAIO Mesh Properties"
    bl_context = "data"

    @staticmethod
    def draw_chunk_properties(
        layout: bpy.types.UILayout,
        mesh_properties: SAIO_Mesh):

        header, body = layout.panel("saio_mesh_chunk")
        header.label(text="Chunk Output")
        if not body:
            return

        body.use_property_split = True
        body.use_property_decorate = False

        col_prop(body, mesh_properties, "override_chunk_output")

        type_layout = body.column()
        type_layout.active = mesh_properties.override_chunk_output

        col_prop(type_layout, mesh_properties, "volume_mesh")
        type_layout.separator(type="LINE")

        type_layout.prop(mesh_properties, "chunk_vertex_contents")

        if mesh_properties.chunk_vertex_contents != 'AUTO':
            type_layout.prop(mesh_properties, "chunk_vertex_format")
        
        nonweight_layout = type_layout.column()
        nonweight_layout.active = mesh_properties.chunk_vertex_type == 'AUTO' or mesh_properties.chunk_vertex_type in WEIGHTED_VERTEX_CHUNKS
        col_prop(nonweight_layout, mesh_properties, "force_binary_weights")

        vertex_user_attrib_layout = type_layout.column()
        vertex_user_attrib_layout.active = mesh_properties.chunk_vertex_type in USER_ATTRIBUTE_VERTEX_CHUNKS
        vertex_user_attrib_layout.prop(mesh_properties, "chunk_vertex_attributes")

        type_layout.separator(type="LINE")

        type_layout.prop(mesh_properties, "chunk_polygon_attributes_mode")
        type_layout.prop(mesh_properties, "chunk_polygon_attributes_1")

        poly_attrib_2_layout = type_layout.column()
        poly_attrib_2_layout.active = mesh_properties.chunk_polygon_attributes_mode != 'MERGED_SINGLE'
        poly_attrib_2_layout.prop(mesh_properties, "chunk_polygon_attributes_2")

        poly_attrib_3_layout = type_layout.column()
        poly_attrib_3_layout.active = mesh_properties.chunk_polygon_attributes_mode != 'SINGLE_MERGED'
        poly_attrib_3_layout.prop(mesh_properties, "chunk_polygon_attributes_3")


    @staticmethod
    def draw_mesh_properties(
            layout: bpy.types.UILayout,
            file_format: str,
            mesh_properties: SAIO_Mesh):

        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(mesh_properties, "normals_mode")
        layout.prop(mesh_properties, "color_mode")
        col_prop(layout, mesh_properties, "no_bounds")

        if file_format == 'CHUNK':
            SAIO_PT_Mesh.draw_chunk_properties(layout, mesh_properties)


    # === overriden methods === #

    @classmethod
    def poll(cls, context):
        return cls.verify(context) is None

    @classmethod
    def verify(cls, context: bpy.types.Context):
        if context.active_object is None:
            return "No active object"

        if context.active_object.type != 'MESH':
            return "Active object not a mesh"

        return None

    def draw_panel(self, context):

        SAIO_PT_Mesh.draw_mesh_properties(
            self.layout,
            context.scene.saio_scene.file_format,
            context.active_object.data.saio_mesh)
            