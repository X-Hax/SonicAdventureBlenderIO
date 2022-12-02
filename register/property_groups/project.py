import bpy
from bpy.props import (
    EnumProperty,
    StringProperty
)


class SAIO_Project(bpy.types.PropertyGroup):
    """Stores info related to SA Project Files"""

    project_file_path: StringProperty(
        name="SA Project File: ",
        default=""
    )

    project_folder: StringProperty(
        name="SA Project Folder",
        default=""
    )

    data_files: EnumProperty(
        name="Data Files",
        items=()
    )

    mdl_files: EnumProperty(
        name="Mdl Files",
        items=()
    )

    mod_name: StringProperty(
        name="Mod name",
        default=""
    )

    mod_author: StringProperty(
        name="Mod Author",
        default=""
    )

    mod_description: StringProperty(
        name="Mod Description",
        default=""
    )

    mod_version: StringProperty(
        name="Mod Version",
        default=""
    )

    @classmethod
    def register(cls):
        pass
