"""Object properties"""

import bpy
from bpy.props import (
    BoolProperty,
    PointerProperty
)


class SAIO_Node(bpy.types.PropertyGroup):
    """NJS_OBJECT Flag Settings and event entry properties"""

    ignore_position: BoolProperty(
        name="Ignore Position",
        description="Ignores object position.",
        default=False
    )

    ignore_rotation: BoolProperty(
        name="Ignore Rotation",
        description="Ignores object rotation.",
        default=False
    )

    ignore_scale: BoolProperty(
        name="Ignore Scale",
        description="Ignores object scale.",
        default=False
    )

    rotate_zyx: BoolProperty(
        name="Rotate ZYX",
        description="Sets rotation mode to ZYX order.",
        default=False
    )

    skip_draw: BoolProperty(
        name="Skip Draw",
        description="Skips drawing the model.",
        default=False
    )

    skip_children: BoolProperty(
        name="Skip Children",
        description="Skips any child nodes of the current node.",
        default=False
    )

    no_animate: BoolProperty(
        name="Not Animated",
        description="Whether the node is ignored by animations",
        default=False
    )

    no_morph: BoolProperty(
        name="No Morph",
        description="Whether the node is ignored by morphs",
        default=False
    )

    @classmethod
    def register(cls):
        bpy.types.Object.saio_node = PointerProperty(type=cls) # pylint: disable=assignment-from-no-return
        bpy.types.Bone.saio_node = PointerProperty(type=cls) # pylint: disable=assignment-from-no-return
        bpy.types.EditBone.saio_node = PointerProperty(type=cls) # pylint: disable=assignment-from-no-return

    @staticmethod
    def get_active_node_properties(
            context: bpy.types.Context | None
    ) -> tuple[str, 'SAIO_Node'] | None:

        if context is None:
            context = bpy.context

        obj = context.active_object

        if (obj is None
                or obj.type not in ['MESH', 'ARMATURE', 'EMPTY']):
            return None

        if obj.type == "ARMATURE":
            if obj.mode == "POSE":
                obj = obj.data.bones.active
            elif obj.mode == "EDIT":
                obj = obj.data.edit_bones.active

        if obj is None:
            return None
        return (obj.name, obj.saio_node)
