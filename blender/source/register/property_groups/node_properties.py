import bpy
from bpy.props import (
    BoolProperty,
    PointerProperty
)

class SAIO_Node(bpy.types.PropertyGroup):

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

    clip: BoolProperty(
        name="Clip",
        description="If the mesh bounds are out of view, skip children when rendering",
        default=False
    )

    cache_rotation: BoolProperty(
        name="Cache rotation",
        description="Cache rotation data before the object is processed. (Not supported by every game)",
        default=False
    )

    apply_cached_rotation: BoolProperty(
        name="Apply Cached Rotation",
        description="Use cached rotation data. (Not supported by every game)",
        default=False
    )

    @classmethod
    def register(cls):
        bpy.types.Object.saio_node = PointerProperty(type=cls) # pylint: disable=assignment-from-no-return
        bpy.types.Bone.saio_node = PointerProperty(type=cls) # pylint: disable=assignment-from-no-return
        bpy.types.EditBone.saio_node = PointerProperty(type=cls) # pylint: disable=assignment-from-no-return