import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    PointerProperty
)

from ...utility.general import get_addon_preferences

MESH_DATA_TYPES = {'MESH', 'CURVE', 'TEXTCURVE', 'SURFACE'}
WEIGHTED_VERTEX_CHUNKS = {'BLANK', 'DIFFUSE', 'NORMAL'}

CHUNK_VERTEX_TYPES_BASE = [
    ('AUTO', "Determine which vertex chunk type to use based on the included vertex data"),
    None,
    ('BLANK',      "Position-only vertices (supports weights)"),
    ('BLANK4',     "Position-only vertices, XYZW positions (GPU ready)"),
    ('USER_ATTR',  ""),
    None,
    ('DIFFUSE',      "Diffuse colors (BGRA8) (supports weights)"),
    ('DIFF_SPEC',    "Diffuse colors (BGRA8), Specular colors (BGRA8)"),
    ('DIFF_SPEC_4',  "Diffuse colors (RGB565), Specular colors (RGB565)"),
    ('DIFF_SPEC_5',  "Diffuse colors (BGRA4), Specular colors (RGB565)"),
    ('INTENSITY',    "16-bit Intensity (diffuse and specular)"),
    None,
    ('NORMAL',            "Normals (Supports weights)"),
    ('NORMAL4',           "XYZW positions, XYZW normals (GPU ready)"),
    ('NORMAL_USER_ATTR',  "Normals, User attributes"),
    None,
    ('NORMAL_DIFFUSE',      "Normals, Diffuse colors (BGRA8)"),
    ('NORMAL_DIFF_SPEC_4',  "Normals, Diffuse colors (RGB565), Specular colors (RGB565)"),
    ('NORMAL_DIFF_SPEC_5',  "Normals, Diffuse colors (BGRA4), Specular colors (RGB565)"),
    ('NORMAL_INTENSITY',    "32-bit packed normals, 16-bit Intensity (diffuse and specular)"),
    None,
    ('NORMAL32',            "32-bit packed normals"),
    ('NORMAL32_DIFFUSE',    "32-bit packed normals, diffuse colors (BGRA8)"),
    ('NORMAL32_USER_ATTR',  "32-bit packed normals, user attributes")
]

CHUNK_VERTEX_TYPE_NAMES = [
    "Automatic",
    None,
    "Position-only (Weightable)",
    "Position-only (XYZW)",
    "Position-only, User attributes",
    None,
    "Diffuse (Weightable)",
    "Diffuse, Specular (8888)",
    "Diffuse, Specular (4444, 565)",
    "Diffuse, Specular (565,  565)",
    "Diffuse, Specular (Intensity)",
    None,
    "Normals (Weightable)",
    "Normals (XYZW)",
    "Normals, User attributes",
    None,
    "Normals, Diffuse (8888)",
    "Normals, Diffuse, Specular (4444, 565)",
    "Normals, Diffuse, Specular (565,  565)",
    "Normals, Diffuse, Specular (Intensity)",
    None,
    "Packed normals",
    "Packed normals, Diffuse (8888)",
    "Packed normals, User attributes"
]

CHUNK_VERTEX_TYPE_NJ_NAMES = [
    "Automatic",
    None,
    "CV / CV_NF",
    "CV_SH",
    "CV_UF",
    None,
    "CV_D8 / CV_NF_D8",
    "CV_D8_S8",
    "CV_S5",
    "CV_S4",
    "CV_IN",
    None,
    "CV_VN / CV_VN_NF",
    "CV_VN_SH",
    "CV_VN_UF",
    None,
    "CV_VN_D8",
    "CV_VN_S5",
    "CV_VN_S4",
    "CV_VN_IN ",
    None,
    "CV_VNX",
    "CV_VNX_D8",
    "CV_VNX_UF"
]

CHUNK_VERTEX_TYPES = []

def _get_chunk_vertex_types(saio_mesh, context: bpy.types.Context):
    pref = get_addon_preferences(context)
    names = CHUNK_VERTEX_TYPE_NJ_NAMES if pref.use_ninja_vertex_type_names else CHUNK_VERTEX_TYPE_NAMES

    if len(CHUNK_VERTEX_TYPES) == 0 or CHUNK_VERTEX_TYPES[-1][1] != names[-1]:
        CHUNK_VERTEX_TYPES.clear()

        index = 1
        for base, name in zip(CHUNK_VERTEX_TYPES_BASE, names):
            if base is None:
                CHUNK_VERTEX_TYPES.append(None)
                continue

            CHUNK_VERTEX_TYPES.append((base[0], name, base[1], index))
            index += 1


    return CHUNK_VERTEX_TYPES


class SAIO_Mesh(bpy.types.PropertyGroup):

    vertex_chunk_type: EnumProperty(
        name="Vertex chunk type",
        description="The type of vertex chunk to use when exporting",
        items=_get_chunk_vertex_types,
        default=1
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