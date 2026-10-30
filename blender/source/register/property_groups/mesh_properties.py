import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    PointerProperty
)

from ...utility.general import get_addon_preferences

MESH_DATA_TYPES = {'MESH', 'CURVE', 'TEXTCURVE', 'SURFACE'}
WEIGHTED_VERTEX_CHUNKS = {'BLANK', 'DIFFUSE', 'NORMAL'}

CHUNK_VERTEX_TYPES = [
    ('AUTO',                "Automatic",                               "Determine which vertex chunk type to use based on the included vertex data", 1),
    None,
    ('BLANK',               "Position-only (Supports Weights)",        "Position-only vertices", 2),
    ('BLANK4',              "Position-only (XYZW)",                    "Position-only vertices, XYZW positions (GPU ready)", 3),
    None,
    ('USER_ATTR',           "User attributes",                         "User attributes", 4),
    None,
    ('DIFFUSE',             "Diffuse (8888) (Supports Weights)",       "Diffuse colors (BGRA8)", 5),
    None,
    ('DIFF_SPEC',           "Diffuse, Specular (8888)",                "Diffuse colors (BGRA8), Specular colors (BGRA8)", 6),
    ('DIFF_SPEC_4',         "Diffuse, Specular (4444, 565)",           "Diffuse colors (RGB565), Specular colors (RGB565)", 7),
    ('DIFF_SPEC_5',         "Diffuse, Specular (565, 565)",            "Diffuse colors (BGRA4), Specular colors (RGB565)", 8),
    ('INTENSITY',           "Diffuse, Specular (Intensity)",           "16-bit Intensity (diffuse and specular)", 9),
    None,
    ('NORMAL',              "Normals (Supports Weights)",              "Normals (Supports weights)", 10),
    ('NORMAL4',             "Normals (XYZW)",                          "XYZW positions, XYZW normals (GPU ready)", 11),
    ('NORMAL32',            "Normals (Packed)",                          "32-bit packed normals", 12),
    None,
    ('NORMAL_DIFFUSE',      "Normals, Diffuse (8888)",                 "Normals, Diffuse colors (BGRA8)", 13),
    ('NORMAL32_DIFFUSE',    "Normals, Diffuse (Packed, 8888)",          "32-bit packed normals, diffuse colors (BGRA8)", 14),
    None,
    ('NORMAL_DIFF_SPEC_4',  "Normals, Diffuse, Specular (4444, 565)",  "Normals, Diffuse colors (RGB565), Specular colors (RGB565)", 15),
    ('NORMAL_DIFF_SPEC_5',  "Normals, Diffuse, Specular (565, 565)",   "Normals, Diffuse colors (BGRA4), Specular colors (RGB565)", 16),
    ('NORMAL_INTENSITY',    "Normals, Diffuse, Specular (Intensity)",  "32-bit packed normals, 16-bit Intensity (diffuse and specular)", 17),
    None,
    ('NORMAL_USER_ATTR',    "Normals, User attributes",                "Normals, User attributes", 18),
    ('NORMAL32_USER_ATTR',  "Packed normals, User attributes",         "32-bit packed normals, user attributes", 19),
    None,
    ('ERROR', "ERROR", "Invalid vertex type? Please contact a developer!", 256)
]

CHUNK_VERTEX_TYPE_LUT = {}
for type in CHUNK_VERTEX_TYPES:
    if type is not None:
        CHUNK_VERTEX_TYPE_LUT[type[3]] = type[0]
        CHUNK_VERTEX_TYPE_LUT[type[0]] = type[3]

CHUNK_VERTEX_CONTENTS = [
    ("AUTO", "Automatic", "Determine off the mesh contents"),
    ("BLANK", "Position-only", "Vertices are made of positions and nothing more"),
    ("USER_ATTR", "User Attributes", "Vertices have user attributes"),
    ("DIFFUSE", "Diffuse", "Vertices have diffuse colors"),
    ("DIFF_SPEC", "Diffuse, Specular", "Vertices have diffuse and specular colors"),
    ("NORMAL", "Normals", "Vertices have normals"),
    ("NRM_DIFF", "Normals, Diffuse", "Vertices have normals and diffuse colors"),
    ("NRM_DIFF_SPEC", "Normals, Diffuse, Specular", "Vertices have normals, diffuse and specular colors"),
    ("NRM_USER_ATTR", "Normals, User Attributes", "Vertices have normals and vertex attributes")
]

CHUNK_VERTEX_FORMAT_ASSIGNMENTS = {
    "AUTO": { 1 },
    "BLANK": { 2, 3 },
    "USER_ATTR": { 4 },
    "DIFFUSE": { 5 },
    "DIFF_SPEC": { 6, 7, 8, 9 },
    "NORMAL": { 10, 11, 12 },
    "NRM_DIFF": { 13, 14 },
    "NRM_DIFF_SPEC": { 15, 16, 17 },
    "NRM_USER_ATTR": { 18, 19 },
    "ERROR": { 256 }
}

def _get_vertex_contents(saio_mesh):
    type_index = CHUNK_VERTEX_TYPE_LUT[saio_mesh.chunk_vertex_type]

    for i, contents in enumerate(CHUNK_VERTEX_CONTENTS):
        assigned = CHUNK_VERTEX_FORMAT_ASSIGNMENTS[contents[0]]
        
        if type_index in assigned:
            return i
        
    return 0

def _set_vertex_contents(saio_mesh, value: int):
    assigned = CHUNK_VERTEX_FORMAT_ASSIGNMENTS[CHUNK_VERTEX_CONTENTS[value][0]]
    type_index = CHUNK_VERTEX_TYPE_LUT[saio_mesh.chunk_vertex_type]
    
    if type_index not in assigned:
        new_value = min(assigned)
        saio_mesh.chunk_vertex_type = CHUNK_VERTEX_TYPE_LUT[new_value]        

CHUNK_VERTEX_FORMATS = []

def _get_vertex_format_items(saio_mesh, context: bpy.types.Context):
    type_index = CHUNK_VERTEX_TYPE_LUT[saio_mesh.chunk_vertex_type]
    
    for assignment in CHUNK_VERTEX_FORMAT_ASSIGNMENTS.values():
        if type_index in assignment:
            break

    CHUNK_VERTEX_FORMATS.clear()
    CHUNK_VERTEX_FORMATS.extend([item for item in CHUNK_VERTEX_TYPES if item is not None and item[3] in assignment])
    return CHUNK_VERTEX_FORMATS

def _get_vertex_format(saio_mesh):
    return CHUNK_VERTEX_TYPE_LUT[saio_mesh.chunk_vertex_type]

def _set_vertex_format(saio_mesh, value: int):
    saio_mesh.chunk_vertex_type = CHUNK_VERTEX_TYPE_LUT[value]


class SAIO_Mesh(bpy.types.PropertyGroup):

    override_chunk_output: BoolProperty(
        name="Override Output Type",
        description="Enables manually setting the output type, instead of using the export type settings",
        default=False
    )

    volume_mesh: BoolProperty(
        name="Volume mesh",
        description="Whether this mesh is a volume mesh",
        default=False
    )

    chunk_vertex_type: EnumProperty(
        name="(Internal) Vertex type",
        description="The internal vertex chunk type; Used when exporting",
        items=CHUNK_VERTEX_TYPES,
        default="AUTO"
    )

    chunk_vertex_contents: EnumProperty(
        name="Vertex contents",
        description="The type of vertex chunk to use when exporting",
        items=CHUNK_VERTEX_CONTENTS,
        get=_get_vertex_contents,
        set=_set_vertex_contents
    )

    chunk_vertex_format: EnumProperty(
        name="Vertex format",
        description="Formatting of the vertex contents",
        items=_get_vertex_format_items,
        get=_get_vertex_format,
        set=_set_vertex_format
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