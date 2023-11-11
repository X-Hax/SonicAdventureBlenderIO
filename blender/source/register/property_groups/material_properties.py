"""Material property group"""

import bpy
from bpy.props import (
    BoolProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    EnumProperty,
    PointerProperty
)

from ...utility.material_setup import update_material_values


def _update_material_values(self, context):
    path = repr(self)
    if (not path.startswith("bpy.data.materials['")
            or not path.endswith("'].saio_material")):
        return
    material_name = path[20:-16]
    material = bpy.data.materials[material_name]

    sceneprops = context.scene.saio_scene
    blend_method = sceneprops.viewport_alpha_type
    clip_threshold = sceneprops.viewport_alpha_cutoff
    enable_backface_culling = sceneprops.enable_backface_culling

    if material is not None:
        update_material_values(
            material, blend_method, clip_threshold, enable_backface_culling)


class SAIO_Material(bpy.types.PropertyGroup):
    """ Property Group for managing Material Properties"""

    # ===== Color properties =====

    diffuse: FloatVectorProperty(
        name="Diffuse Color",
        description="Color of the material",
        subtype='COLOR_GAMMA',
        size=4,
        min=0.0, max=1.0,
        update=_update_material_values,
        default=(1.0, 1.0, 1.0, 1.0),
    )

    specular: FloatVectorProperty(
        name="Specular Color",
        description="Color of the Specular",
        subtype='COLOR_GAMMA',
        size=4,
        min=0.0, max=1.0,
        update=_update_material_values,
        default=(1.0, 1.0, 1.0, 1.0),
    )

    ambient: FloatVectorProperty(
        name="Ambient Color",
        description="Ambient Color (SA2 only)",
        subtype='COLOR_GAMMA',
        size=4,
        min=0.0, max=1.0,
        update=_update_material_values,
        default=(1.0, 1.0, 1.0, 1.0),
    )

    specular_exponent: IntProperty(
        name="Specular Exponent",
        description="Specular exponent on the material",
        default=32,
        min=0, max=255,
        update=_update_material_values,
    )

    flat_shading: BoolProperty(
        name="Flat Shading",
        description="Render without shading",
        update=_update_material_values,
        default=False
    )

    ignore_ambient: BoolProperty(
        name="No Ambient Lighting",
        description="Ignores ambient as a whole when rendering (SA2 Only)",
        update=_update_material_values,
        default=False
    )

    ignore_diffuse: BoolProperty(
        name="Ignore Diffuse Lighting",
        description="Ignores diffuse lighting when rendering",
        update=_update_material_values,
        default=False
    )

    ignore_specular: BoolProperty(
        name="Ignore Specular Lighting",
        description="Removes the specularity from the material",
        update=_update_material_values,
        default=False
    )

    # ===== Blending properties =====

    use_alpha: BoolProperty(
        name="Use Alpha",
        description=(
            "Utilizes the alpha channel of the"
            " color and texture to render transparency"
        ),
        update=_update_material_values,
        default=False
    )

    double_sided: BoolProperty(
        name="Double Sided",
        description=(
            "On collision: Makes polygons collidable from both side."
            " On render: disables backface culling"
            " (only working using render-altering mods)"),
        update=_update_material_values,
        default=True
    )

    source_alpha: EnumProperty(
        name="Source Alpha",
        description="Destination Alpha",
        items=(
            ('ZERO', 'Zero', ""),
            ('ONE', 'One', ""),
            ('OTHER', 'Other', ""),
            ('INV_OTHER', 'Inverted other', ""),
            ('SRC', 'Source', ""),
            ('INV_SRC', 'Inverted source', ""),
            ('DST', 'Destination', ""),
            ('INV_DST', 'Inverted destination', ""),
        ),
        default='SRC'
    )

    destination_alpha: EnumProperty(
        name="Destination Alpha",
        description="Destination Alpha",
        items=(
            ('ZERO', 'Zero', ""),
            ('ONE', 'One', ""),
            ('OTHER', 'Other', ""),
            ('INV_OTHER', 'Inverted other', ""),
            ('SRC', 'Source', ""),
            ('INV_SRC', 'Inverted source', ""),
            ('DST', 'Destination', ""),
            ('INV_DST', 'Inverted destination', ""),
        ),
        default='INV_SRC'
    )

    # ===== Texture properties =====

    texture_id: IntProperty(
        name="Texture ID",
        description="ID of the texture in the PVM/GVM to use",
        default=0,
        min=0
    )

    use_texture: BoolProperty(
        name="Use Texture",
        description="Uses the texture references in the properties",
        update=_update_material_values,
        default=False
    )

    use_environment: BoolProperty(
        name="Environment mapping",
        description=(
            "Uses normal mapping instead of the uv coordinates,"
            "to make the texture face the camera (equivalent to matcaps)"
        ),
        update=_update_material_values,
        default=False
    )

    texture_filtering: EnumProperty(
        name="Filter Type",
        description="The texture filter",
        items=(('POINT', 'Point', "no filtering"),
               ('BILINEAR', 'Bilinear', "Bilinear Filtering"),
               ('TRILINEAR', 'Trilinear', "Trilinear Filtering"),
               ('BLEND', 'Blend',
                "Bi- and Trilinear Filtering blended together")
               ),
        default='BILINEAR'
    )

    anisotropic_filtering: BoolProperty(
        name="Anisotropic filtering",
        description="Enable Anisotropy for the texture of the material",
        default=True
    )

    mipmap_distance_multiplier: FloatProperty(
        name="MipMap distance multiplier",
        description=(
            "mipmap distance multiplier;"
            " Gets rounded to steps of 0.25"
        ),
        default=0,
        min=0,
        max=3.75
    )

    clamp_u: BoolProperty(
        name="Clamp U",
        description=(
            "The U channel of the mesh UVs"
            " always stays between 0 and 1"
        ),
        update=_update_material_values,
        default=False
    )

    clamp_v: BoolProperty(
        name="Clamp V",
        description=(
            "The V channel of the mesh UVs"
            " always stays between 0 and 1"
        ),
        update=_update_material_values,
        default=False
    )

    mirror_u: BoolProperty(
        name="Mirror U",
        description=(
            "The V channel of the mesh UVs"
            " mirrors every time it reaches a multiple of 1"
        ),
        update=_update_material_values,
        default=False
    )

    mirror_v: BoolProperty(
        name="Mirror V",
        description=(
            "The V channel of the mesh UVs"
            " mirrors every time it reaches a multiple of 1"
        ),
        update=_update_material_values,
        default=False
    )

    # ===== GC properties =====

    shadow_stencil: IntProperty(
        name="Shadow Stencil",
        description="shadow stencil",
        min=0, max=0xF,
        default=1
    )

    texgen_coord_id: EnumProperty(
        name="Texcoord ID (output slot)",
        description=(
            "Determines in which slot the generated"
            " coordinates should be saved, so that they can be used"
        ),
        items=(
            ('TEXCOORD0', 'TexCoord0', ""),
            ('TEXCOORD1', 'TexCoord1', ""),
            ('TEXCOORD2', 'TexCoord2', ""),
            ('TEXCOORD3', 'TexCoord3', ""),
            ('TEXCOORD4', 'TexCoord4', ""),
            ('TEXCOORD5', 'TexCoord5', ""),
            ('TEXCOORD6', 'TexCoord6', ""),
            ('TEXCOORD7', 'TexCoord7', ""),
            ('TEXCOORDMAX', 'TexCoordMax', ""),
            ('TEXCOORDNULL', 'TexCoordNull', ""),
        ),
        default='TEXCOORD0'
    )

    texgen_type: EnumProperty(
        name="Generation Type",
        description="Which function to use when generating the coords",
        items=(
            ('MATRIX3X4', 'Matrix 3x4', ""),
            ('MATRIX2X4', 'Matrix 2x4', ""),
            ('BITMAP0', 'Bitmap 0', ""),
            ('BITMAP1', 'Bitmap 1', ""),
            ('BITMAP2', 'Bitmap 2', ""),
            ('BITMAP3', 'Bitmap 3', ""),
            ('BITMAP4', 'Bitmap 4', ""),
            ('BITMAP5', 'Bitmap 5', ""),
            ('BITMAP6', 'Bitmap 6', ""),
            ('BITMAP7', 'Bitmap 7', ""),
            ('SRTG', 'SRTG', ""),
        ),
        default='MATRIX2X4'
    )

    texgen_source: EnumProperty(
        name="Generation Source",
        description=(
            "Which data of the mesh to use when"
            " generating the uv coords"
        ),
        items=(
            ('POSITION', 'Position', ""),
            ('NORMAL', 'Normal', ""),
            ('BINORMAL', 'Binormal', ""),
            ('TANGENT', 'Tangent', ""),
            ('TEX0', 'Tex0', ""),
            ('TEX1', 'Tex1', ""),
            ('TEX2', 'Tex2', ""),
            ('TEX3', 'Tex3', ""),
            ('TEX4', 'Tex4', ""),
            ('TEX5', 'Tex5', ""),
            ('TEX6', 'Tex6', ""),
            ('TEX7', 'Tex7', ""),
            ('TEXCOORD0', 'TexCoord0', ""),
            ('TEXCOORD1', 'TexCoord1', ""),
            ('TEXCOORD2', 'TexCoord2', ""),
            ('TEXCOORD3', 'TexCoord3', ""),
            ('TEXCOORD4', 'TexCoord4', ""),
            ('TEXCOORD5', 'TexCoord5', ""),
            ('TEXCOORD6', 'TexCoord6', ""),
            ('COLOR0', 'Color0', ""),
            ('COLOR1', 'Color1', ""),
        ),
        default='TEX0'
    )

    texgen_matrix_id: EnumProperty(
        name="Matrix ID",
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

    @classmethod
    def register(cls):
        bpy.types.Material.saio_material = PointerProperty(type=cls)
