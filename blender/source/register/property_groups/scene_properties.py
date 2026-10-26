import bpy
from bpy.props import (
    EnumProperty,
    StringProperty,
)

from ...utility.general import get_addon_preferences

_FILE_FORMATS = (
    ("BASIC", "Basic", ""),
    ("CHUNK", "Chunk", ""),
    ("GINJA", "Ginja", "")
)

_FILE_FORMAT_LUT = {}
for index, item in enumerate(_FILE_FORMATS):
    _FILE_FORMAT_LUT[item[0]] = index

def _get_file_format_items(saio_scene, context: bpy.types.Context):
    pref = get_addon_preferences(context)
    if pref.enable_ginja or saio_scene.internal_file_format == 'GINJA':
        return _FILE_FORMATS
    else:
        return (
            ("BASIC", "Basic", ""),
            ("CHUNK", "Chunk", "")
        )
    
def _get_file_format(saio_scene):
    return _FILE_FORMAT_LUT[saio_scene.internal_file_format]

def _set_file_format(saio_scene, value):
    saio_scene.internal_file_format = _get_file_format_items(saio_scene, bpy.context)[value][0]

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

    internal_file_format: EnumProperty(
        name="File format (internal)",
        description="Determines the file output format",
        items=(
            ("BASIC", "Basic", ""),
            ("CHUNK", "Chunk", ""),
            ("GINJA", "Ginja", "")
        ),
        default="CHUNK"
    )

    file_format: EnumProperty(
        name="Scene format",
        description="Determines the file output format",
        items=_get_file_format_items,
        get=_get_file_format,
        set=_set_file_format
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