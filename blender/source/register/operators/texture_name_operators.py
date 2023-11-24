import os

from bpy.props import (
    EnumProperty,
    StringProperty,
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

from ..property_groups.texturename_properties import SAIO_TextureNameList

from ...dotnet import load_dotnet, SA3D_Texturing


class TextureNameOperator(SAIOBaseOperator):
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
            world = context.scene.saio_scene.texturename_world
        elif context.active_object is not None:
            world = context.active_object.saio_texturename_world

        if world is None:
            return None
        return world.saio_texturename_list

    def _execute(self, context):
        texture_names = self.get_texture_list(context)
        if texture_names is not None:
            self.list_execute(context, texture_names) # pylint: disable=no-member
        return {'FINISHED'}


class SAIO_OT_TextureNames_Add(TextureNameOperator, ListAdd):
    bl_idname = "saio.texturenames_add"
    bl_label = "Add a texture name"
    bl_description = "Adds name to the texture name list"


class SAIO_OT_TextureNames_Remove(TextureNameOperator, ListRemove):
    bl_idname = "saio.texturenames_remove"
    bl_label = "Remove a texture name"
    bl_description = "Removes the selected name from the texture name list"


class SAIO_OT_TextureNames_Move(TextureNameOperator, ListMove):
    bl_idname = "saio.texturenames_move"
    bl_label = "Move texture name"
    bl_description = "Moves a texture name in list"


class SAIO_OT_TextureNames_Clear(TextureNameOperator, ListClear):
    bl_idname = "saio.texturenames_clear"
    bl_label = "Clear list"
    bl_description = "Removes all entries from the list"


class SAIO_OT_TextureNames_Import(
        TextureNameOperator, SAIOBaseFileLoadOperator):
    bl_idname = "saio.texturenames_import"
    bl_label = "Import texture list"
    bl_description = "Import texture names of a .satex or .tls file"

    filter_glob: StringProperty(
        default="*.satex;*.tls;",
        options={'HIDDEN'},
    )

    def list_execute(self, context, texture_names: SAIO_TextureNameList): # pylint: disable=unused-argument
        load_dotnet()

        from ...importing import i_texture

        njs_texlist = SA3D_Texturing.TEXTURE_NAME_LIST.ReadFromTextFile(self.filepath)
        i_texture.process_texture_names(njs_texlist, texture_names)


class SAIO_OT_TextureNames_Export(
        TextureNameOperator, SAIOBaseFileSaveOperator):
    bl_idname = "saio.texturenames_export"
    bl_label = "Export texture list"
    bl_description = "Export texture name list to a .satex file"

    filename_ext = '.satex'

    def list_execute(self, context, texture_names: SAIO_TextureNameList): # pylint: disable=unused-argument
        load_dotnet()
        from ...exporting import o_texture

        filename = os.path.basename(self.filepath)
        njs_list = o_texture.create_texnames_from_names(
            texture_names, filename)
        njs_list.WriteAsIniToTextFile(self.filepath)
