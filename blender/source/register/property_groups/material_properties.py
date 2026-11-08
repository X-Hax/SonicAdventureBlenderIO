import bpy
from bpy.props import (
    BoolProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    EnumProperty,
    PointerProperty
)

from .ginja_material_properties import SAIO_Material_Ginja

def _get_uv_range(self):
    return 1 if self.uv_precision_level >= 2 else 0

def _set_uv_range(self, enum_index):
    self.uv_precision_level = 2 if enum_index == 1 else 0

class SAIO_Material(bpy.types.PropertyGroup):
    """ Property Group for managing Material Properties"""

    # ===== Rendering properties =====

    double_sided: BoolProperty(
        name="Double Sided",
        description=(
            "On collision: Makes polygons collidable from both side."
            " On render: disables backface culling"),
        default=False
    )

    rendering_model: EnumProperty(
        name="Rendering model",
        description="How the model is rendered",
        items=(
            ("SMOOTH", "Smooth (Gouraud)", "Calculates output information per vertex and transitions between them on the triangle"),
            ("FLAT", "Flat", "Calculates output information for a single vertex and uses that across the whole triangle")
        ),
        default="SMOOTH"
    )

    # ===== Shading properties =====

    ignore_lighting: BoolProperty(
        name="Ignore Lighting",
        description="Renders surface with no diffuse lighting (effectively turns ambient color white)",
        default=False
    )

    ignore_ambient: BoolProperty(
        name="Ignore Ambient",
        description="Ignores ambient as a whole when rendering",
        default=False
    )

    ignore_specular: BoolProperty(
        name="Ignore Specular",
        description="Removes the specularity from the material",
        default=False
    )

    specular_exponent: FloatProperty(
        name="Specular Exponent",
        description="Specular exponent on the material",
        default=11,
        min=0, max=255,
    )


    # ===== Transparency properties =====

    alpha_mode: EnumProperty(
        name="Alpha mode",
        description="How to utilize the alpha channel of the diffuse color and/or texture",
        items=(
            ("OPAQUE", "Opaque", "No transparency"),
            ("TRANSPARENT", "Transparent", "Automatic transparency"),
            ("FORCE_CLIP_ON", "Transparent (Force clip on)", "Transparency with clipping force enabled"),
            ("FORCE_CLIP_OFF", "Transparent (Force clip off)", "Transparency with clipping force disabled"),
        ),
        default="OPAQUE"
    )

    source_blendmode: EnumProperty(
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

    destination_blendmode: EnumProperty(
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


    # ===== Color properties =====

    diffuse: FloatVectorProperty(
        name="Diffuse Color",
        description="Color of the material",
        subtype='COLOR_GAMMA',
        size=4,
        min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
    )

    ambient: FloatVectorProperty(
        name="Ambient Color",
        description="Ambient Color (SA2 only)",
        subtype='COLOR_GAMMA',
        size=4,
        min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
    )

    specular: FloatVectorProperty(
        name="Specular Color",
        description="Color of the Specular",
        subtype='COLOR_GAMMA',
        size=3,
        min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0),
    )


    # ===== Texture properties =====

    use_texture: BoolProperty(
        name="Use Texture",
        description="Whether to render a texture on the mesh",
        default=False
    )

    texture_id: IntProperty(
        name="Texture ID",
        description="ID of the texture in the texture archive to use",
        default=0,
        min=0
    )

    texture_filtering: EnumProperty(
        name="Filter mode",
        description="The texture filter",
        items=(
            ('NEAREST', 'Nearest', "no interpolation"),
            ('BILINEAR', 'Bilinear', "Bilinear interpolation"),
            ('TRILINEAR', 'Trilinear', "Trilinear interpolation")
        ),
        default='BILINEAR'
    )

    anisotropic_filtering: BoolProperty(
        name="Anisotropic filtering",
        description="Enable Anisotropy for the texture of the material",
        default=False,
        
    )

    mipmap_distance_multiplier: FloatProperty(
        name="MipMap distance multiplier",
        description=(
            "mipmap distance multiplier;"
            " Gets rounded to steps of 0.25"
        ),
        default=1,
        min=0,
        max=3.75,
        step=25
    )
    
    texturing_mode: EnumProperty(
        name="Texturing mode",
        items=(
            ("UV", "UV Mapped", "Map the texture using texture coordinates"),
            ("ENV", "Environment Mapped", "Project the texture against the model based on its normals (or positions, if there are no normals)")
        ),
        default="UV"
    )

    env_include_uvs: BoolProperty(
        name="Include UVs",
        description="When enabling \"environment mapped\", UVs are not exported. Enable this to export them regardless"
    )


    uv_precision_level: IntProperty(
        name="UV precision level",
        description=(
            "How precise the UV coordinates should be stored."
            " Each step doubles precision but halfs the maximum range."
            " - BASIC only supports 0"
            " - CHUNK only supports 0 and 2"
        ),
        min=0, max=7,
        default=0
    )

    uv_range: EnumProperty(
        name="UV Range",
        description="The range with which UVs are exported",
        items=(
            ("UVN", "UVN (0-256)", ""),
            ("UVH", "UVH (0-1024)", "")
        ),
        get=_get_uv_range,
        set=_set_uv_range
    )

    clamp_u: BoolProperty(
        name="Clamp U",
        description=(
            "The U channel of the mesh UVs always stays between 0 and 1"
        ),
        default=False
    )

    clamp_v: BoolProperty(
        name="Clamp V",
        description=(
            "The V channel of the mesh UVs always stays between 0 and 1"
        ),
        default=False
    )

    mirror_u: BoolProperty(
        name="Mirror U",
        description=(
            "The V channel of the mesh UVs mirrors every time it reaches a multiple of 1"
        ),
        default=False
    )

    mirror_v: BoolProperty(
        name="Mirror V",
        description=(
            "The V channel of the mesh UVs mirrors every time it reaches a multiple of 1"
        ),
        default=False
    )


    # ===== Ginja =====

    ginja_properties: PointerProperty(
        type=SAIO_Material_Ginja
    )

    @classmethod
    def register(cls):
        bpy.types.Material.saio_material = PointerProperty(type=cls)