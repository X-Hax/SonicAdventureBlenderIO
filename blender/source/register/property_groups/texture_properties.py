import os
import bpy
from bpy.props import (
    IntProperty,
    StringProperty,
    EnumProperty,
    PointerProperty,
    CollectionProperty
)
from .base_list import BaseList


class SAIO_Texture(bpy.types.PropertyGroup):

    image: PointerProperty(
        type=bpy.types.Image,
        name="Image"
    )

    name: StringProperty(
        name="Slot name",
        description="The name of the slot",
        maxlen=0x28,
        default=""
    )

    global_index: IntProperty(
        name="Global Index",
        description="The global texture id in the texture file",
        default=0,
        min=0
    )

    override_width: IntProperty(
        name="Override Width",
        description="Width of the texture to replace. Set 0 to not override",
        default=0,
        min=0
    )

    override_height: IntProperty(
        name="Override Height",
        description="Height of the texture to replace. Set 0 to not override",
        default=0,
        min=0
    )

    texture_type: EnumProperty(
        name="Type",
        description="Texture type",
        items=(
            ("RGBA", "Colored", "Image is used as is"),
            ("ID4", "Index4", "Image is used as a 4-bit palett mask"),
            ("ID8", "Index8", "Image is used as a 8-bit palett mask"),
        ),
        default="RGBA"
    )

    @property
    def index(self):
        path = repr(self)
        end = path.rfind(".")
        path = path[:end]
        textures = self.path_resolve(path)

        for index, texture in enumerate(textures):
            if texture == self:
                return index

        raise Exception("Texture has no index")

    @classmethod
    def register(cls):
        pass


class SAIO_TextureList(BaseList):

    elements: CollectionProperty(
        type=SAIO_Texture,
        name="Texture List",
        description="The textures used by sonic adventure"
    )

    @classmethod
    def _get_index_comparator(cls, value):
        if isinstance(value, str):
            return lambda x: x.name == value
        elif isinstance(value, SAIO_Texture):
            return lambda x: x == value
        elif isinstance(value, bpy.types.Image):
            return lambda x: x.image == value
        raise NotImplementedError()

    def _on_created(self, value, **args):
        # getting next usable global id
        ids = [t.global_index for t in self]
        ids.sort(key=lambda x: x)

        global_index = len(self)
        for i, index in enumerate(ids):
            if i != index:
                global_index = i
                break
        value.global_index = global_index

        if "image" in args:
            value.image = args["image"]

        if "name" in args:
            value.name = args["name"]
        elif value.image is not None:
            value.name = os.path.splitext(value.image.name)[0]
        else:
            value.name = "Texture"

    def _on_clear(self):
        for t in self:
            if t.image is not None:
                t.image.use_fake_user = False

    def autoname(self):
        for tex in self:
            if tex.image is not None:
                tex.name = os.path.splitext(tex.image.name)[0]
            else:
                tex.name = "Texture"

    @ classmethod
    def register(cls):
        bpy.types.World.saio_texture_list = PointerProperty(
            type=cls,
            name="SAIO Texture Lists"
        )

        bpy.types.Object.saio_texture_world = PointerProperty(
            type=bpy.types.World,
            name="SAIO Texture World",
            description="Used as texture list storage"
        )
