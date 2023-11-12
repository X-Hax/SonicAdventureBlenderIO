from typing import Union
import bpy

from ..register.property_groups.texture_properties import (
    SAIO_Texture,
    SAIO_TextureList,
)

from ..register.property_groups.texturename_properties import (
    SAIO_TextureNameList
)


class CompiledTexlist:

    textures: list[SAIO_Texture]

    def __init__(self):
        self.textures = []

    @staticmethod
    def from_tex_list(texture_list: SAIO_TextureList):
        result = CompiledTexlist()

        for texture in texture_list:
            result.textures.append(texture)

        return result

    @staticmethod
    def from_tex_name(
            texture_list: SAIO_TextureList,
            texture_names: SAIO_TextureNameList):
        result = CompiledTexlist()

        for texname in texture_names:
            name: str = texname.name.strip().lower()

            texture = None
            for check_tex in texture_list:
                if check_tex.name.lower() == name:
                    texture = check_tex
                    break

            result.textures.append(texture)

        return result

    def get_index(self, value: Union[str, SAIO_Texture, bpy.types.Image]):

        if isinstance(value, str):
            def check(tex):
                return tex.name == value
        elif isinstance(value, SAIO_Texture):
            def check(tex):
                return tex == value
        elif isinstance(value, bpy.types.Image):
            def check(tex):
                return tex.image == value

        for i, tex in enumerate(self.textures):
            if check(tex):
                return i

        return None


class TexlistManager:

    _root_texlist: CompiledTexlist

    _compiled_tex_lists: dict[SAIO_TextureList, CompiledTexlist]
    _texname_strings: dict[SAIO_TextureNameList, str]
    _compiled_tex_name_lists: dict[str, CompiledTexlist]

    _list_mapping: dict[CompiledTexlist, set[bpy.types.Material]]
    _material_mapping: dict[bpy.types.Material, CompiledTexlist]

    def __init__(self):
        self._root_texlist = None
        self._texname_strings = {}
        self._compiled_tex_name_lists = {}
        self._compiled_tex_lists = {}
        self._list_mapping = {}
        self._material_mapping = {}

    def _get_compiled_tex_list(
            self,
            texture_list: SAIO_TextureList,
            texture_names: SAIO_TextureNameList):

        if texture_list is None:
            return None

        if texture_names is None:

            if texture_list not in self._compiled_tex_lists:
                compiled_list = CompiledTexlist.from_tex_list(texture_list)
                self._compiled_tex_lists[texture_list] = compiled_list
            else:
                compiled_list = self._compiled_tex_lists[texture_list]

        else:

            # getting the texname string
            if texture_names not in self._texname_strings:
                texname_string = ""
                for texname in texture_names:
                    texname_string += texname.name.strip()
                self._texname_strings[texture_names] = texname_string
            else:
                texname_string = self._texname_strings[texture_names]

            # getting the texture list dictionary
            if texture_list not in self._compiled_tex_name_lists:
                tl_dict = {}
                self._compiled_tex_name_lists[texture_list] = {}
            else:
                tl_dict = self._compiled_tex_name_lists[texture_list]

            # getting the compiled list
            if texname_string not in tl_dict:
                compiled_list = CompiledTexlist.from_tex_name(
                    texture_list, texture_names)
                tl_dict[texname_string] = compiled_list
            else:
                compiled_list = tl_dict[texname_string]

        return compiled_list

    def _eval_obj_materials(
            self,
            obj: bpy.types.Object,
            texture_list: SAIO_TextureList,
            texture_names: SAIO_TextureNameList,
            compiled_list: CompiledTexlist):

        texture_world = obj.saio_texture_world
        texturename_world = obj.saio_texturename_world

        recompile = False
        if (texture_world is not None
                and len(texture_world.saio_texture_list) > 0):
            texture_list = texture_world.saio_texture_list
            recompile = True

        if (texturename_world is not None
                and len(texturename_world.saio_texturename_list) > 0):
            texture_names = texturename_world.saio_texturename_list
            recompile = True

        if recompile:
            compiled_list = self._get_compiled_tex_list(
                texture_list, texture_names)

        if obj.type == 'MESH':
            if compiled_list not in self._list_mapping:
                material_list = set()
                self._list_mapping[compiled_list] = material_list
            else:
                material_list = self._list_mapping[compiled_list]

            material_list.update(obj.data.materials)

        for child in obj.children:
            self._eval_obj_materials(
                child, texture_list, texture_names, compiled_list)

    def evaluate_texlists(self, scene: bpy.types.Scene):

        texture_list = None
        texture_names = None
        saio = scene.saio_scene

        if saio.texture_list is not None and len(saio.texture_list) > 0:
            texture_list = saio.texture_list

        if (saio.texturename_list is not None
                and len(saio.texturename_list) > 0):
            texture_names = saio.texturename_list

        self._root_texlist = self._get_compiled_tex_list(
            texture_list, texture_names)

        all_materials = set()
        for material_list in self._list_mapping.values():
            all_materials.update(material_list)

        for material in all_materials:
            compiled_list = None
            for key, material_list in self._list_mapping.items():
                if material not in material_list:
                    if compiled_list is not None:
                        compiled_list = self._root_texlist
                        break
                    else:
                        compiled_list = key

            self._material_mapping[material] = compiled_list

    def get_material_texlist(self, material: bpy.types.Material):
        if material in self._material_mapping:
            return self._material_mapping[material]
        return self._root_texlist
