"""Object properties"""

import bpy
from bpy.props import (
    BoolProperty,
    PointerProperty
)


class SAIO_Node(bpy.types.PropertyGroup):
    """NJS_OBJECT Flag Settings"""

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
        description=(
            "Sets if the node is counted in "
            "the hierarchy for animations."
        ),
        default=False
    )

    no_morph: BoolProperty(
        name="No Morph",
        description="Sets if the node can have morph effect applied.",
        default=False
    )

    @classmethod
    def register(cls):
        bpy.types.Object.saio_node = PointerProperty(type=cls)
        bpy.types.Bone.saio_node = PointerProperty(type=cls)
        bpy.types.EditBone.saio_node = PointerProperty(type=cls)
        bpy.types.Armature.saio_node = PointerProperty(type=cls)
