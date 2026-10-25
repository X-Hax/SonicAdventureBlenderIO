import bpy
from bpy.props import (
    BoolProperty,
    IntProperty,
    EnumProperty
)

class SAIO_Material_Ginja(bpy.types.PropertyGroup):

    vertex_color_for_diffuse: BoolProperty(
        name="Vertex color for diffuse",
        description="Use vertex colors for the diffuse mesh color (ginja only)",
        default=True
    )

    vertex_color_for_ambient: BoolProperty(
        name="Vertex color for ambient",
        description="Use vertex colors for the ambient mesh color (ginja only)",
        default=False
    )

    texture_slot: IntProperty(
        name="Texture slot",
        description="The texture slot to use (ginja only)",
        min=0, max=3,
        default=0
    )

    # ===== Tev stage =====

    tevstg_manual: BoolProperty(
        name="Manual Tev stage",
        description="Manually specify how the tev stage parameter should be set up"
    )

    tevstg_stage: IntProperty(
        name="Tev stage",
        description="Ginja tev stage",
        min=0, max=7,
        default=0
    )

    tevstg_tex_coord: IntProperty(
        name="Tev stage texture coordinates",
        description="Ginja tev stage texture coordinates",
        min=0, max=7,
        default=0
    )

    tevstg_tex_map: IntProperty(
        name="Tev stage texture map",
        description="Ginja tev stage texture map",
        min=0, max=7,
        default=0
    )

    tevstg_color_channel: EnumProperty(
        name="Tev stage color channel",
        description="Ginja tev stage color channel (output destination)",
        items=(
            ("COLOR0", "Color 0", ""),
            ("COLOR1", "Color 1", ""),
            ("ALPHA0", "Alpha 0", ""),
            ("ALPHA1", "Alpha 1", ""),
            ("COLOR0A0", "Color+Alpha 0", ""),
            ("COLOR1A1", "Color+Alpha 1", ""),
            ("COLORZERO", "Color Zero", ""),
            ("ALPHABUMP", "Alpha Bump", ""),
            ("ALPHABUMPN", "Alpha Bump N", ""),
        ),
        default="COLOR0A0"
    )

    # ===== Tex gen =====

    texgen_manual: BoolProperty(
        name="Manual Tex gen",
        description="Manually specify how the tex gen parameter should be set up"
    )

    texgen_tex_coord: IntProperty(
        name="Tev stage texture coordinates",
        description="Destination texture coordinates",
        min=0, max=7,
        default=0
    )

    texgen_type: EnumProperty(
        name="Tex gen type",
        description="Which function to use when generating the coords",
        items=(
            ('MATRIX3X4', 'Matrix 3x4', ""),
            ('MATRIX2X4', 'Matrix 2x4', ""),
            ('BUMP0', 'Bump 0', ""),
            ('BUMP1', 'Bump 1', ""),
            ('BUMP2', 'Bump 2', ""),
            ('BUMP3', 'Bump 3', ""),
            ('BUMP4', 'Bump 4', ""),
            ('BUMP5', 'Bump 5', ""),
            ('BUMP6', 'Bump 6', ""),
            ('BUMP7', 'Bump 7', ""),
            ('SRTG', 'SRTG', ""),
        ),
        default='MATRIX2X4'
    )

    texgen_source: EnumProperty(
        name="Tex gen source",
        description=(
            "Which data of the mesh to use when generating the uv coords"
        ),
        items=(
            ('POSITION', 'Position', ""),
            ('NORMAL', 'Normal', ""),
            ('BINORMAL', 'Binormal', ""),
            ('TANGENT', 'Tangent', ""),
            ('TEXCOORD0', 'Texcoord 0', ""),
            ('TEXCOORD1', 'Texcoord 1', ""),
            ('TEXCOORD2', 'Texcoord 2', ""),
            ('TEXCOORD3', 'Texcoord 3', ""),
            ('TEXCOORD4', 'Texcoord 4', ""),
            ('TEXCOORD5', 'Texcoord 5', ""),
            ('TEXCOORD6', 'Texcoord 6', ""),
            ('TEXCOORD7', 'Texcoord 7', ""),
            ('BUMPTEXCOORD0', 'Bump TexCoord 0', ""),
            ('BUMPTEXCOORD1', 'Bump TexCoord 1', ""),
            ('BUMPTEXCOORD2', 'Bump TexCoord 2', ""),
            ('BUMPTEXCOORD3', 'Bump TexCoord 3', ""),
            ('BUMPTEXCOORD4', 'Bump TexCoord 4', ""),
            ('BUMPTEXCOORD5', 'Bump TexCoord 5', ""),
            ('BUMPTEXCOORD6', 'Bump TexCoord 6', ""),
            ('COLOR0', 'Color 0', ""),
            ('COLOR1', 'Color 1', ""),
        ),
        default='TEXCOORD0'
    )

    texgen_matrix_id: EnumProperty(
        name="Tex gen matrix",
        description=(
            "If gentype is matrix, then this property defines which user"
            " defined matrix to use"
        ),
        items=(
            ('MATRIX0', 'Matrix 0', ""),
            ('MATRIX1', 'Matrix 1', ""),
            ('MATRIX2', 'Matrix 2', ""),
            ('MATRIX3', 'Matrix 3', ""),
            ('MATRIX4', 'Matrix 4', ""),
            ('MATRIX5', 'Matrix 5', ""),
            ('MATRIX6', 'Matrix 6', ""),
            ('MATRIX7', 'Matrix 7', ""),
            ('MATRIX8', 'Matrix 8', ""),
            ('MATRIX9', 'Matrix 9', ""),
            ('IDENTITY', 'Identity', "")
        ),
        default='IDENTITY'
    )