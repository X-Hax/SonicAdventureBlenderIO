import bpy

from ..property_groups import (
    mesh as nj_mesh
)


class SAIO_PT_Mesh(bpy.types.Panel):
    bl_label = "SAIO Mesh Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_options = {"DEFAULT_CLOSED"}

    @staticmethod
    def draw_mesh_properties(
            layout: bpy.types.UILayout,
            mesh_properites: nj_mesh.SAIO_Mesh):

        layout.prop(mesh_properites, "force_vertex_colors")

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == 'MESH'
        )

    def draw(self, context):

        SAIO_PT_Mesh.draw_mesh_properties(
            self.layout,
            context.active_object.data.saio_mesh)
