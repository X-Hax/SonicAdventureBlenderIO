import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    PointerProperty
)

MESH_DATA_TYPES = {'MESH', 'CURVE', 'TEXTCURVE', 'SURFACE'}
WEIGHTED_VERTEX_CHUNKS = {'BLANK', 'DIFFUSE', 'NORMAL'}

class SAIO_Mesh(bpy.types.PropertyGroup):

    vertex_chunk_type: EnumProperty(
        name="Vertex chunk type",
        description="The type of vertex chunk to use when exporting",
        items=(
            ('AUTO', "Automatic", "Determine which vertex chunk type to use based on the included vertex data"),
            None,
            ('BLANK', "Blank (Supports weights)", "Vertices only have position data"),
            ('BLANK4', "Blank (4 Components)", "Vertices only have 4-component position data (4th component is always 1)"),
            ('USER_ATTR', "User attributes", ""),
            None,
            ('DIFFUSE', "Diffuse (BGRA8) (Supports weights)", ""),
            ('DIFF_SPEC', "Diffuse (BGRA8), Specular (BGRA8)", ""),
            ('DIFF_SPEC_5', "Diffuse (RGB565), Specular (RGB565)", ""),
            ('DIFF_SPEC_4', "Diffuse (BGRA4), Specular (RGB565)", ""),
            ('INTENSITY', "Intensity", "Vertices have 16 bit intensity values for diffuse and specular colors"),
            None,
            ('NORMAL', "Normals (Supports weights)", ""),
            ('NORMAL4', "Normals (4 Components)", "Vertices have 4-component position and normal data (4th component is always 1 for positions and 0 for normals)"),
            ('NORMAL_USER_ATTR', "Normals, User attributes", ""),
            None,
            ('NORMAL_DIFFUSE', "Normals, Diffuse (BGRA8)", ""),
            ('NORMAL_DIFF_SPEC_5', "Normals, Diffuse (RGB565), Specular (RGB565)", ""),
            ('NORMAL_DIFF_SPEC_4', "Normals, Diffuse (BGRA4), Specular (RGB565)", ""),
            ('NORMAL_INTENSITY', "Normals, Intensity", "Vertices have normals and 16 bit intensity values for diffuse and specular colors"),
            None,
            ('NORMAL32', "Normals (32-bit Packed)", "Vertices have 32-bit packed normals"),
            ('NORMAL32_DIFFUSE', "Normals (32-bit Packed), Diffuse (BGRA8)", "Vertices have 32-bit packed normals and diffuse colors"),
            ('NORMAL32_USER_ATTR', "Normals (32-bit Packed), User attributes", "Vertices have 32-bit packed normals and user attributes")
        ),
        default="AUTO"
    )

    high_precision_weights: BoolProperty(
        name="High precision weights",
        description="Use 16 bit weights instead of 8 bit weights",
        default=False
    )

    force_binary_weights: BoolProperty(
        name="Force binary weights",
        description="Force the model to use binary weights, if it would otherwise use regular weights",
        default=False
    )

    normals_mode: EnumProperty(
        name="Normals mode",
        description="Determines whether normals are included in export",
        items=(
            ('AUTO', "Automatic", "Only includes normals if no vertex color is present"),
            ('INCLUDE', "Include", "Always include normals in the export"),
            ('EXCLUDE', "Exclude", "Never include normals in the export"),
        ),
        default="AUTO"
    )

    color_mode: EnumProperty(
        name="Color mode",
        description="Determines whether color are included in export",
        items=(
            ('AUTO', "Automatic", "Automatically includes vertex colors if the mesh has them"),
            ('INCLUDE', "Include", "Always include vertex colors in the export"),
            ('EXCLUDE', "Exclude", "Never include vertex colors in the export"),
        ),
        default="AUTO"
    )

    no_bounds: BoolProperty(
        name="No Bounds",
        description=(
            "Disable calculation of mesh bounds on export."
            " Effectively disables frustrum culling of the mesh ingame"
            " (does not affect weighted models)"
        ),
        default=False
    )

    @classmethod
    def register(cls):
        bpy.types.Mesh.saio_mesh = PointerProperty(type=cls) # pylint: disable=assignment-from-no-return