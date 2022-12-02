import bpy
from bpy.props import (
    IntProperty,
    PointerProperty,
    CollectionProperty
)
from .base_list import BaseList


class SAIO_EventNode_UVAnim(bpy.types.PropertyGroup):

    material_index: IntProperty(
        name="Material Index",
        description="Index of the material on this model to animate",
        default=0
    )


class SAIO_EventNode_UVAnimList(BaseList):

    elements: CollectionProperty(
        type=SAIO_EventNode_UVAnim,
        name="UV Animations"
    )

    @ classmethod
    def register(cls):
        bpy.types.Object.saio_eventnode_uvanims = PointerProperty(
            type=cls,
            name="SAIO Event Node UV Aims"
        )
