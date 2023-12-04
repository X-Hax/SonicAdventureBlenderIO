import bpy
from bpy.props import (
    BoolProperty,
    IntProperty,
    PointerProperty
)


class SAIO_Mesh(bpy.types.PropertyGroup):

    force_vertex_colors: BoolProperty(
        name="Force Vertex colors",
        description=(
            "When a deform model, a binary weighted mesh"
            " with vertex colors will be forced"
        ),
        default=False
    )

    texcoord_precision_level: IntProperty(
        name="Texcoord precision level",
        description=(
            "Some formats allow for a higher UV precision at the cost of reduced range."
            "Every level has twice the precision of the previous level."),
        default=0,
        min=0,
        max=7
    )

    @classmethod
    def register(cls):
        bpy.types.Mesh.saio_mesh = PointerProperty(type=cls) # pylint: disable=assignment-from-no-return
