import bpy
from bpy.props import (
    EnumProperty,
    StringProperty,
)

class SAIO_Scene(bpy.types.PropertyGroup):
    author: StringProperty(
        name="Author",
        description="The creator of this file",
        default="",
    )

    description: StringProperty(
        name="Description",
        description="A Description of the file contents",
        default="",
    )

    file_format: EnumProperty(
        name="Scene format",
        description="Determines the file output format",
        items=(
            ("BASIC", "Basic", ""),
            ("CHUNK", "Chunk", ""),
            ("GINJA", "Ginja", "")
        ),
        default="CHUNK"
    )

    scene_type: EnumProperty(
        name="Scene type",
        description="Enables specific SAIO tools for the scene.",
        items=[
            ("MDL", "Model", "Model file"),
            #("LVL", "Landtable", "Landtable file"),
            #("EVR", "SA2 Event Root", "SA2 Event root/base scene"),
            #("EVC", "SA2 Event Scene", "SA2 Event cut/sub scene"),
        ],
        default="MDL"
    )

    @classmethod
    def register(cls):
        bpy.types.Scene.saio_scene = bpy.props.PointerProperty(type=cls) # pylint: disable=assignment-from-no-return