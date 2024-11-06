import bpy

from .base_panel import PropertiesPanel

from ..property_groups.mesh_properties import SAIO_Mesh


class SAIO_PT_Mesh(PropertiesPanel):
    bl_label = "SAIO Mesh Properties"
    bl_context = "data"

    @staticmethod
    def draw_mesh_properties(
            layout: bpy.types.UILayout,
            mesh_properties: SAIO_Mesh):

        layout.prop(mesh_properties, "force_vertex_colors")
        layout.prop(mesh_properties, "texcoord_precision_level")
        layout.prop(mesh_properties, "no_bounds")

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
            context.active_object.data.saio_mesh)
