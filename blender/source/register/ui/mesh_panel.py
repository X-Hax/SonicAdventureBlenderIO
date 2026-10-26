import bpy
from .base_panel import PropertiesPanel
from ..property_groups.mesh_properties import SAIO_Mesh, WEIGHTED_VERTEX_CHUNKS
from ...utility.draw import col_prop


class SAIO_PT_Mesh(PropertiesPanel):
    bl_label = "SAIO Mesh Properties"
    bl_context = "data"

    @staticmethod
    def draw_mesh_properties(
            layout: bpy.types.UILayout,
            file_format: str,
            mesh_properties: SAIO_Mesh):

        layout.use_property_split = True
        layout.use_property_decorate = False

        if file_format == 'CHUNK':
            layout.prop(mesh_properties, "vertex_chunk_type")

            weight_layout = layout.column()
            weight_layout.active = mesh_properties.vertex_chunk_type == 'AUTO' or mesh_properties.vertex_chunk_type in WEIGHTED_VERTEX_CHUNKS
            col_prop(weight_layout, mesh_properties, "high_precision_weights")

            nonweight_layout = layout.column()
            nonweight_layout.active = mesh_properties.vertex_chunk_type == 'AUTO' or mesh_properties.vertex_chunk_type not in WEIGHTED_VERTEX_CHUNKS
            col_prop(nonweight_layout, mesh_properties, "force_binary_weights")
            layout.separator(type="LINE")

        layout.prop(mesh_properties, "normals_mode")
        layout.prop(mesh_properties, "color_mode")
        col_prop(layout, mesh_properties, "no_bounds")

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