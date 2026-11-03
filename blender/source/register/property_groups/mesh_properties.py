import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    PointerProperty,
    StringProperty
)

MESH_DATA_TYPES = {'MESH', 'CURVE', 'TEXTCURVE', 'SURFACE'}
WEIGHTED_VERTEX_CHUNKS = {'BLANK', 'DIFFUSE', 'NORMAL'}
USER_ATTRIBUTE_VERTEX_CHUNKS = {'USER_ATTR', 'NORMAL_USER_ATTR', 'NORMAL32_USER_ATTR'}

CHUNK_VERTEX_TYPES = (
    ('AUTO',                "AUTO",                "", 1),
    ('BLANK',               "BLANK",               "", 2),
    ('BLANK4',              "BLANK4",              "", 3),
    ('USER_ATTR',           "USER_ATTR",           "", 4),
    ('DIFFUSE',             "DIFFUSE",             "", 5),
    ('DIFF_SPEC',           "DIFF_SPEC",           "", 6),
    ('DIFF_SPEC_4',         "DIFF_SPEC_4",         "", 7),
    ('DIFF_SPEC_5',         "DIFF_SPEC_5",         "", 8),
    ('INTENSITY',           "INTENSITY",           "", 9),
    ('NORMAL',              "NORMAL",              "", 10),
    ('NORMAL4',             "NORMAL4",             "", 11),
    ('NORMAL32',            "NORMAL32",            "", 12),
    ('NORMAL_DIFFUSE',      "NORMAL_DIFFUSE",      "", 13),
    ('NORMAL32_DIFFUSE',    "NORMAL32_DIFFUSE",    "", 14),
    ('NORMAL_DIFF_SPEC_4',  "NORMAL_DIFF_SPEC_4",  "", 15),
    ('NORMAL_DIFF_SPEC_5',  "NORMAL_DIFF_SPEC_5",  "", 16),
    ('NORMAL_INTENSITY',    "NORMAL_INTENSITY",    "", 17),
    ('NORMAL_USER_ATTR',    "NORMAL_USER_ATTR",    "", 18),
    ('NORMAL32_USER_ATTR',  "NORMAL32_USER_ATTR",  "", 19),
    ('ERROR',               "ERROR",               "", 256)
)

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

CHUNK_VERTEX_FORMATS = {
    "AUTO": ( ('AUTO', "Automatic", "Determine which vertex chunk type to use based on the included vertex data", 1), ),

    "BLANK": (
        ('BLANK',   "Float3 (Supports Weights)",  "Position-only vertices", 2),
        ('BLANK4',  "Float4 (XYZ+W)",             "Position-only vertices, XYZW positions (GPU ready)", 3),
    ),

    "USER_ATTR": (
        ('USER_ATTR',  "Int32",  "32-Bit user attributes", 4),
    ),

    "DIFFUSE": (
        ('DIFFUSE',  "ARGB 8888 (Supports Weights)", "", 5),
    ),

    "DIFF_SPEC": (
        ('DIFF_SPEC',    "ARGB 8888, RGB 888",          "", 6),
        ('DIFF_SPEC_4',  "RGB 565, RGB 565",            "", 7),
        ('DIFF_SPEC_5',  "ARGB 4444, RGB 565",          "", 8),
        ('INTENSITY',    "Intensity 16, Intensity 16",  "", 9),
    ),

    "NORMAL": (
        ('NORMAL',    "Float3 (Supports Weights)",  "", 10),
        ('NORMAL4',   "Float4 (XYZ+W)",             "XYZW positions, XYZW normals (GPU ready)", 11),
        ('NORMAL32',  "Packed32",                   "", 12),
    ),

    "NRM_DIFF": (
        ('NORMAL_DIFFUSE',   "Float3, ARGB 8888",    "", 13),
        ('NORMAL32_DIFFUSE', "Packed32, ARGB 8888",  "", 14),
    ),

    "NRM_DIFF_SPEC": (
        ('NORMAL_DIFF_SPEC_4',  "Float3, RGB 565, RGB 565",            "", 15),
        ('NORMAL_DIFF_SPEC_5',  "Float3, ARGB 4444, RGB 565",          "", 16),
        ('NORMAL_INTENSITY',    "Float3, Intensity 16, Intensity 16",  "", 17),
    ),

    "NRM_USER_ATTR": (
        ('NORMAL_USER_ATTR',    "Float3, Int32",    "", 18),
        ('NORMAL32_USER_ATTR',  "Packed32, Int32",  "", 19),
    ),

    "ERROR": ( ('ERROR', "ERROR", "Invalid vertex type? Please contact a developer!", 256), )
}

CHUNK_VERTEX_FORMAT_ASSIGNMENTS = {}
for contents, items in CHUNK_VERTEX_FORMATS.items():
    CHUNK_VERTEX_FORMAT_ASSIGNMENTS[contents] = set([item[3] for item in items])

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

CURRENT_CHUNK_VERTEX_FORMATS = []

def _get_vertex_format_items(saio_mesh, context: bpy.types.Context):
    return CHUNK_VERTEX_FORMATS[saio_mesh.chunk_vertex_contents]

def _get_vertex_format(saio_mesh):
    return CHUNK_VERTEX_TYPE_LUT[saio_mesh.chunk_vertex_type]

def _set_vertex_format(saio_mesh, value: int):
    saio_mesh.chunk_vertex_type = CHUNK_VERTEX_TYPE_LUT[value]


class SAIO_Mesh(bpy.types.PropertyGroup):

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

    ##################################################

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

    chunk_vertex_attributes: StringProperty(
        name="Vertex user attribute container",
        description="Name of the blender attribute container for vertex user attributes"
    )

    chunk_polygon_attributes_mode: EnumProperty(
        name="Polygon attribute mode",
        description="How to utilize attributes",
        items=(
            ('SINGLE', "Single, Single, Single", "Use one container per attribute"),
            ('MERGED_SINGLE', "Merged, Single", "Use one container for attributes 1 and 2, and one for attributes 3"),
            ('SINGLE_MERGED', "Single, Merged", "Use one container for attributes 1, and one for attributes 2 and 3"),
        )
    )

    chunk_polygon_attributes_1: StringProperty(
        name="Polygon attribute 1 container",
        description="Name of the blender attribute container for the first set of per-polygon attributes"
    )

    chunk_polygon_attributes_2: StringProperty(
        name="Polygon attribute 2 container",
        description="Name of the blender attribute container for the second set of per-polygon attributes"
    )

    chunk_polygon_attributes_3: StringProperty(
        name="Polygon attribute 3 container",
        description="Name of the blender attribute container for the third set of per-polygon attributes"
    )

    @classmethod
    def register(cls):
        bpy.types.Mesh.saio_mesh = PointerProperty(type=cls) # pylint: disable=assignment-from-no-return