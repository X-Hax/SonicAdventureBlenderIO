
import bpy
from bpy.props import (
    BoolProperty,
    FloatProperty,
    StringProperty,
)


class SAIO_LandTable(bpy.types.PropertyGroup):
    """Landtable specific properties"""

    name: StringProperty(
        name="Name",
        description=(
            "The label for the landtable in the file."
            " If empty, the filename will be used"
        ),
        default=""
    )

    draw_distance: FloatProperty(
        name="Draw Distance",
        description=(
            "How far the camera has to be away"
            " from an object to render (only sa2lvl)"
        ),
        default=3000
    )

    double_sided_collision: BoolProperty(
        name="Double-Sided Collision",
        description=(
            "Enables double sided collision detection."
            " This is supposed to be used as a failsafe"
            " for people unexperienced with how normals work"
        ),
        default=False
    )

    tex_file_name: StringProperty(
        name="Texture Filename",
        description=(
            "The name of the texture file specified"
            " in the landtable info (lvl format)"
        ),
        default=""
    )

    tex_list_pointer: StringProperty(
        name="Texture List Pointer (hex)",
        description="Used for when replacing a stage and its textures",
        default="0"
    )
