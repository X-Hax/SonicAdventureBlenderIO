import bpy
from bpy.props import (
    StringProperty,
    PointerProperty,
    CollectionProperty
)
from .base_list import BaseList


class SAIO_TextureName(bpy.types.PropertyGroup):

    name: StringProperty(
        name="Name of the texture",
        description="The name of the texture",
        default=""
    )

    @classmethod
    def register(cls):
        pass


class SAIO_TextureNameList(BaseList):

    elements: CollectionProperty(
        type=SAIO_TextureName,
        name="Texture Names List",
        description="The texture names used by the object/scene"
    )

    @classmethod
    def _get_index_comparator(cls, value):
        if isinstance(value, str):
            return lambda x: x.name == value
        elif isinstance(value, SAIO_TextureName):
            return lambda x: x == value
        raise NotImplementedError()

    def _on_created(self, value, **args):
        if "name" in args:
            value.name = args["name"]
        else:
            value.name = "Texture"

    @classmethod
    def register(cls):
        bpy.types.World.saio_texturename_list = PointerProperty(
            type=cls,
            name="SAIO Texture Lists"
        )

        bpy.types.Object.saio_texturename_world = PointerProperty(
            type=bpy.types.World,
            name="SAIO Texture Name World",
            description="Used as texture name list storage"
        )
