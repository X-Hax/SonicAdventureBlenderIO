import os
import bpy
from bpy.props import (
    IntProperty,
    StringProperty,
    PointerProperty,
    CollectionProperty
)

from typing import Union

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


class SAIO_TextureList(bpy.types.PropertyGroup):

    textures: CollectionProperty(
        type=SAIO_Texture,
        name="Texture List",
        description="The textures used by sonic adventure"
    )

    active_index: IntProperty(
        name="Active texture index",
        description="Index of active item in texture list",
        default=-1
    )

    def get_index(self, value: Union[int, str, SAIO_Texture, bpy.types.Image]):

        if isinstance(value, str):
            def check(tex): return tex.name == value
        elif isinstance(value, SAIO_Texture):
            def check(tex): return tex == value
        elif isinstance(value, bpy.types.Image):
            def check(tex): return tex.image == value

        for i, tex in enumerate(self.textures):
            if check(tex):
                return i

        return None

    def new(
            self,
            name: str = None,
            image: bpy.types.Image = None):

        # getting next usable global id
        ids = [t.global_id for t in self.textures]
        ids.sort(key=lambda x: x)

        global_id = len(self.textures)
        for i, index in enumerate(ids):
            if i != index:
                global_id = i
                break

        # creating texture
        tex = self.textures.add()
        self.active_index = len(self.textures) - 1

        if name is None:
            if image is None:
                name = "Texture"
            else:
                name = os.path.splitext(image.name)[0]

        tex.name = name
        tex.global_id = global_id
        tex.image = image

        return tex

    def remove(self, value: Union[int, str, SAIO_Texture, bpy.types.Image]):
        if isinstance(value, int):
            index = value
        else:
            index = self.get_index(value)

        if index is None or index >= len(self.textures):
            return

        self.textures.remove(index)

        if self.active_index == index:
            self.active_index -= 1

        if len(self.textures) == 0:
            self.active_index = -1
        elif self.active_index < 0:
            self.active_index = 0

    def move(self, old_index: int, new_index: int):
        self.textures.move(
            old_index,
            new_index)

        if self.active_index == old_index:
            self.active_index = new_index

    def autoname(self):
        for tex in self.textures:
            if tex.image is not None:
                tex.name = os.path.splitext(tex.image.name)[0]
            else:
                tex.name = "Texture"

    def clear(self):
        for t in self.textures:
            if t.image is not None:
                t.image.use_fake_user = False
        self.textures.clear()
        self.active_index = -1

    @ classmethod
    def register(cls):
        pass
