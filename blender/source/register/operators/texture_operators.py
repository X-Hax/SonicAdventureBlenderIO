import os
import bpy

from bpy.props import (
    EnumProperty,
    StringProperty
)

from .base_operators import (
    SAIOBaseOperator,
    SAIOBaseFileLoadOperator,
    SAIOBaseFileSaveOperator
)

from .base_list_operators import (
    ListAdd,
    ListRemove,
    ListMove,
    ListClear
)

from ..property_groups.texture_properties import SAIO_TextureList

from ...importing import i_texture
from ...exporting import o_texture
from ...external import SAIONET, CTextureSet
from ...exceptions import SAIODevException

class TextureOperator(SAIOBaseOperator):
    bl_options = {'UNDO'}

    mode: EnumProperty(
        name="Mode",
        items=(
            ("SCENE", "Scene", ""),
            ("OBJECT", "Object", ""),
        ),
        default="SCENE",
        options={'HIDDEN'},
    )

    def get_texture_list(self, context) -> SAIO_TextureList | None:
        world = None
        if self.mode == "SCENE":
            world = context.scene.saio_scene.texture_world
        elif context.active_object is not None:
            world = context.active_object.saio_texture_world

        if world is None:
            return None
        return world.saio_texture_list

    def _execute(self, context):
        texture_list = self.get_texture_list(context)
        if texture_list is not None:
            self.list_execute(context, texture_list)
        return {'FINISHED'}


class SAIO_OT_Textures_Add(TextureOperator, ListAdd):
    bl_idname = "saio.textures_add"
    bl_label = "Add texture"
    bl_description = "Adds texture to the texture list"


class SAIO_OT_Textures_Remove(TextureOperator, ListRemove):
    bl_idname = "saio.textures_remove"
    bl_label = "Remove texture"
    bl_description = "Removes the selected texture from the texture list"


class SAIO_OT_Textures_Move(TextureOperator, ListMove):
    bl_idname = "saio.textures_move"
    bl_label = "Move texture"
    bl_description = "Moves texture slot in list"


class SAIO_OT_Textures_Clear(TextureOperator, ListClear):
    bl_idname = "saio.textures_clear"
    bl_label = "Clear list"
    bl_description = "Removes all entries from the list"


class SAIO_OT_Textures_Autoname(TextureOperator):
    bl_idname = "saio.textures_autoname"
    bl_label = "Autoname entries"
    bl_description = "Renames all entries to the assigned texture"

    def list_execute(
            self,
            context: bpy.types.Context,
            texture_list: SAIO_TextureList):
        texture_list.autoname()


class TextureImportOperator(TextureOperator, SAIOBaseFileLoadOperator):

    def _get_texture_set(self) -> CTextureSet:
        raise NotImplementedError()

    def list_execute(
            self,
            context: bpy.types.Context,
            texture_list: SAIO_TextureList):

        with SAIONET.load():
            try:
                texture_set = self._get_texture_set()
            except Exception:
                self.report({'WARNING'}, "File is not valid!")
                return {'CANCELLED'}

            i_texture.import_texture_set(texture_list, texture_set)


class SAIO_OT_Textures_Import_Archive(TextureImportOperator):
    bl_idname = "saio.textures_importarchive"
    bl_label = "Import Texture archive"

    filter_glob: StringProperty(
        default="*.pak;*.gvm;*.pvm;*.pvmx;*.prs;",
        options={'HIDDEN'},
    )

    def _get_texture_set(self):
        return SAIONET.texture_read_archive_file(self.filepath)


class SAIO_OT_Textures_Import_Pack(TextureImportOperator):
    bl_idname = "saio.textures_importpack"
    bl_label = "Import Texture pack"

    filter_glob: StringProperty(
        default=f"*{os.path.sep}index.txt;",
        options={'HIDDEN'},
    )

    def _get_texture_set(self):
        return SAIONET.texture_import_pack(self.filepath)


class TextureExportOperator(TextureOperator, SAIOBaseFileSaveOperator):
    pass

class SAIO_OT_Textures_Export_Archive(TextureExportOperator):
    bl_idname = "saio.textures_exportarchive"
    bl_label = "Export as texture Archive"

    filename_ext  = ".prs"

    def check(self, context):
        texture_list = self.get_texture_list(context)

        if texture_list.compress:
            extension = '.prs'
        elif texture_list.archive_format == 'PAK':
            extension = '.pak'
        elif texture_list.archive_format == 'GVM':
            extension = '.gvm'
        elif texture_list.archive_format == 'PVM':
            extension = '.pvm'
        elif texture_list.archive_format == 'PVMX':
            extension = '.pvmx'
        else:
            raise SAIODevException("Invalid archive format") 

        no_ext, old_extension = os.path.splitext(self.filepath)

        if old_extension != extension:
            self.filepath = no_ext + extension
            return True

        return False

    def list_execute(
        self,
        context: bpy.types.Context,
        texture_list: SAIO_TextureList):

        with SAIONET.load():
            texture_set = o_texture.create_texture_set(texture_list, None)
            SAIONET.texture_write_archive_file(texture_set, self.filepath)
            
class SAIO_OT_Textures_Export_Pack(TextureExportOperator):
    bl_idname = "saio.textures_exportpack"
    bl_label = "Export as texture pack"

    filename_ext  = ".txt"

    def check(self, context):
        filename = os.path.basename(self.filepath)
        if filename != "index.txt":
            self.filepath = os.path.join(os.path.dirname(self.filepath), "index.txt")
            return True
        return False

    def list_execute(
        self,
        context: bpy.types.Context,
        texture_list: SAIO_TextureList):

        with SAIONET.load():
            texture_set = o_texture.create_texture_set(texture_list, 'PVMX')
            directory_path = os.path.dirname(self.filepath)
            SAIONET.texture_export_pack(texture_set, directory_path)