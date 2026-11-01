import bpy
from .base_panel import PropertiesPanel
from ..property_groups.node_properties import SAIO_Node

from ...utility.draw import col_prop

class SAIO_PT_Node(PropertiesPanel):
    bl_label = "SAIO Node Properties"
    bl_context = "object"

    @staticmethod
    def prop_with_explanation(
        layout: bpy.types.UILayout,
        node_properties: SAIO_Node,
        property: str,
        text: str):

        col_prop(layout, node_properties, property)

        # Texts need to be implemented once 5.3 releases
        # head, body = layout.panel(f"saio_node_{property}", default_closed=True)
        # col_prop(head, node_properties, property)
        # if body:
        #     body.label(text=text)

    @staticmethod
    def draw_node_properties(
            layout: bpy.types.UILayout,
            node_properties: SAIO_Node):

        layout.use_property_split = True
        layout.use_property_decorate = False

        SAIO_PT_Node.prop_with_explanation(layout, node_properties, "no_animate", "Lorem Ipsum")
        SAIO_PT_Node.prop_with_explanation(layout, node_properties, "no_morph", "Lorem Ipsum")
        SAIO_PT_Node.prop_with_explanation(layout, node_properties, "clip", "Lorem Ipsum")
        SAIO_PT_Node.prop_with_explanation(layout, node_properties, "cache_rotation", "Lorem Ipsum")
        SAIO_PT_Node.prop_with_explanation(layout, node_properties, "apply_cached_rotation", "Lorem Ipsum")


    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None and
            context.active_object.type in ['MESH', 'EMPTY', 'ARMATURE']
        )

    def draw(self, context):
        SAIO_PT_Node.draw_node_properties(
            self.layout,
            context.active_object.saio_node
        )


class SAIO_PT_Node_Bone(PropertiesPanel):
    bl_label = "SAIO Node Properties"
    bl_context = "bone"

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return (
            context.bone is not None
            or context.edit_bone is not None
        )

    def draw(self, context):
        bone = context.bone
        if not bone:
            bone = context.edit_bone

        SAIO_PT_Node.draw_node_properties(
            self.layout,
            bone.saio_node,
        )
