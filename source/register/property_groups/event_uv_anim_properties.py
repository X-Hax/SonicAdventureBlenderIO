import bpy
from bpy.props import (
    IntProperty,
    CollectionProperty
)
from .base_list import BaseList


class SAIO_Event_UVAnim(bpy.types.PropertyGroup):

    texture_index: IntProperty(
        name="Texture Index",
        description="Base texture index to animate",
        default=0
    )

    texture_count: IntProperty(
        name="Texture Count",
        description="Texture animation sequence length",
        default=1
    )


class SAIO_Event_UVAnimList(BaseList):

    elements: CollectionProperty(
        type=SAIO_Event_UVAnim,
        name="UV Animations"
    )

    @ classmethod
    def register(cls):
        pass
