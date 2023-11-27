import bpy
from bpy.props import (
    BoolProperty,
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

    @classmethod
    def register(cls):
        bpy.types.Mesh.saio_mesh = PointerProperty(type=cls) # pylint: disable=assignment-from-no-return
