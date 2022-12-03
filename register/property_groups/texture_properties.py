import bpy
from bpy.props import (
    IntProperty,
    StringProperty,
    PointerProperty
)

# Property Group for storing Texture List information.


class SAIO_Texture(bpy.types.PropertyGroup):

    name: StringProperty(
        name="Slot name",
        description="The name of the slot",
        maxlen=0x20,
        default=""
    )

    global_id: IntProperty(
        name="Global ID",
        description="The global texture id in the texture file",
        default=0,
        min=0
    )

    image: PointerProperty(
        type=bpy.types.Image,
        name="Image"
    )

    @classmethod
    def register(cls):
        pass
