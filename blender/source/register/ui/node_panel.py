import bpy
from .base_panel import PropertiesPanel
from ..property_groups.node_properties import SAIO_Node

ATTRIBUTE_LIST = [
    "ignore_position",
    "ignore_rotation",
    "ignore_scale",
    "rotate_zyx",
    "skip_draw",
    "skip_children",
    "no_animate",
    "no_morph",
]

ADVANCED_ATTRIBUTE_LIST = [
    "clip",
    "modifier",
    "use_quaternion_rotation",
    "cache_rotation",
    "apply_cached_rotation",
    "envelope",
]

class SAIO_PT_Node(PropertiesPanel):
    bl_label = "SAIO Node Properties"
    bl_context = "object"

    @staticmethod
    def draw_node_properties(
            layout: bpy.types.UILayout,
            node_properties: SAIO_Node):

        for attribute in ATTRIBUTE_LIST:
            layout.prop(node_properties, attribute)

        header, body = layout.panel(
            "SAIO_node_attributes_advanced", default_closed=True)
        header.label(text="Advanced")

        if body:
            for attribute in ADVANCED_ATTRIBUTE_LIST:
                body.prop(node_properties, attribute)

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
