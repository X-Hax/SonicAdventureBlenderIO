import os
import bpy

from bpy.props import (
    EnumProperty,
    StringProperty,
    BoolProperty
)

from .base import (
    SAIOBaseOperator,
    SAIOBaseFileLoadOperator,
    SAIOBaseFileSaveOperator,
    ListAdd,
    ListRemove,
    ListMove,
    ListClear
)
from ..property_groups.texture_properties import SAIO_TextureList
from ...exporting import o_texture
from ...dotnet import load_dotnet, SA3D_Texturing, SA3D_Archival


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

    def get_texture_list(self, context):
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
            self.list_execute(context, texture_list) # pylint: disable=no-member
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

    def list_execute( # pylint: disable=unused-argument
            self,
            context: bpy.types.Context,
            texture_list: SAIO_TextureList):
        texture_list.autoname()


class TextureImportOperator(TextureOperator, SAIOBaseFileLoadOperator):

    def _get_texture_set(self):
        raise NotImplementedError()

    def list_execute( # pylint: disable=unused-argument
            self,
            context: bpy.types.Context,
            texture_list: SAIO_TextureList):

        load_dotnet()

        try:
            texture_set = self._get_texture_set()
        except Exception:
            self.report({'WARNING'}, "File is not valid!")
            return {'CANCELLED'}

        from ...importing import i_texture
        i_texture.process_texture_set(texture_set, texture_list)


class SAIO_OT_Textures_Import_Pack(TextureImportOperator):
    bl_idname = "saio.textures_importpack"
    bl_label = "Import Texture pack"

    filter_glob: StringProperty(
        default="*.txt;",
        options={'HIDDEN'},
    )

    def _get_texture_set(self):
        folder = os.path.dirname(self.filepath)
        return SA3D_Texturing.TEXTURE_SET.ImportTexturePack(folder)


class SAIO_OT_Textures_Import_Archive(TextureImportOperator):
    bl_idname = "saio.textures_importarchive"
    bl_label = "Import Texture archive"

    filter_glob: StringProperty(
        default="*.pak;*.gvm;*.pvm;*.pvmx;*.prs;",
        options={'HIDDEN'},
    )

    def _get_texture_set(self):
        archive = SA3D_Archival.ARCHIVE.ReadArchiveFromFile(self.filepath)
        return archive.ToTextureSet()


class TextureExportOperator(TextureOperator, SAIOBaseFileSaveOperator):

    def _get_extension(self):
        raise NotImplementedError()

    def _save_texture_set(self, texture_set): # pylint: disable=unused-argument
        raise NotImplementedError()

    def check(self, context):
        extension = self._get_extension()
        no_ext, old_extension = os.path.splitext(self.filepath)

        if old_extension != extension:
            self.filepath = no_ext + extension
            return True

        return False

    def list_execute( # pylint: disable=unused-argument
            self,
            context: bpy.types.Context,
            texture_list: SAIO_TextureList):
        load_dotnet()

        texture_set = o_texture.create_texture_set(texture_list)
        self._save_texture_set(texture_set)


class SAIO_OT_Textures_Export_Archive(TextureExportOperator):
    bl_idname = "saio.textures_exportarchive"
    bl_label = "Export as texture Archive"

    filename_ext = ".prs"

    archive_type: EnumProperty(
        name="Type",
        items=(
            ("PAK", "PAK", "SA2 Pak compressed archive (lossless)"),
            ("PVMX", "PVMX", "Custom SA1 texture archive for (lossless)"),
            ("PVM", "PVM", "Dreamcast texture archive (lossy)"),
            ("GVM", "GVM", "Gamecube texture archvie (lossy)")
        ),
        default="PAK"
    )

    compress: BoolProperty(
        name="Use PRS compression",
        default=False
    )

    def _get_extension(self):
        result = ".prs"

        if not self.compress:
            if self.archive_type == "PAK":
                result = ".pak"
            elif self.archive_type == "PVMX":
                result = ".pvmx"
            elif self.archive_type == "PVM":
                result = ".pvm"
            elif self.archive_type == "GVM":
                result = ".gvm"

        return result

    def _save_texture_set(self, texture_set):

        o_texture.save_texture_archive(
            texture_set,
            self.filepath,
            self.archive_type,
            self.compress)


class SAIO_OT_Textures_Export_Pack(TextureExportOperator):
    bl_idname = "saio.textures_exportpack"
    bl_label = "Export as texture pack"

    filename_ext = ".txt"

    def check(self, context):
        filename = os.path.basename(self.filepath)
        if filename != "index.txt":
            self.filepath = os.path.dirname(self.filepath) + "\\index.txt"
            return True
        return False

    def _get_extension(self):
        return ".txt"

    def _save_texture_set(self, texture_set):
        outdir = os.path.dirname(self.filepath)
        texture_set.ExportTexturePack(outdir)


class SAIO_OT_Texture_ToAssetLibrary(TextureOperator):
    bl_idname = "saio.texture_toassetlibrary"
    bl_label = "Generate Material Asset Library"
    bl_description = (
        "Generates new materials from the texture list and automatically marks"
        " them for the asset library")

    def list_execute(
            self,
            context: bpy.types.Context,
            texture_list: SAIO_TextureList):
        materials: list[bpy.types.Material] = []

        for i, texture in enumerate(texture_list):

            matname = "saio_"

            if texture.image is not None:
                matname += texture.name
            else:
                matname += str(i)

            if matname not in bpy.data.materials:
                material = bpy.data.materials.new(matname)
            else:
                material = bpy.data.materials[matname]

            material.saio_material.use_texture = True
            material.saio_material.texture_id = i

            materials.append(material)

        from ...utility.material_setup import setup_and_update_materials
        setup_and_update_materials(context, materials)

        for m in materials:
            m.asset_mark()
            m.asset_generate_preview()
