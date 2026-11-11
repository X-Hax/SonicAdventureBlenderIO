import os
import bpy
from bpy.props import (
    IntProperty,
    StringProperty,
    EnumProperty,
    PointerProperty,
    CollectionProperty,
    BoolProperty
)
from .base_list import BaseList
from ...exceptions import SAIOException


class SAIO_Texture_GV(bpy.types.PropertyGroup):

    format: EnumProperty(
        name="Format",
        description="How the texture should be encoded",
        items=(
            ('INTENSITY4', "Intensity4", "4 bit grayscale pixel."),
            ('INTENSITY8', "Intensity8", "8 bit grayscale pixel."),
            ('INTENSITYA4', "IntensityA4", "8 bit grayscale + alpha pixel."),
            ('INTENSITYA8', "IntensityA8", "16 bit grayscale + alpha pixel."),
            ('RGB565', "RGB565", "16 bit RGB color pixel"),
            ('RGB5A3', "RGB5A3", "A 16 bit pixel, which is either 15 bits RGB or 15 bits ARGB"),
            ('ARGB8', "ARGB8", "A 32 bit ARGB pixel"),
            ('INDEX4', "Index4", "A 4 bit index pixel that is used in conjunction with a palette."),
            ('INDEX8', "Index8", "An 8 bit index pixel that is used in conjunction with a palette."),
            ('DXT1', "DXT1", "DXT1 block compression pixels. A 4x4 block of pixels is compressed into 16 bytes, where pixels are interpolated."),
        ),
        default='DXT1'
    )

    has_mipmaps: BoolProperty(
        name="Has Mipmaps",
        description="Whether the texture should export with mipmaps",
        default=False
    )

    store_palette: BoolProperty(
        name="Store palette",
        description="If the texture format uses palettes, store the palette generated off the colors for the texture alongside the texture itself",
        default=False
    )

    palette_format: EnumProperty(
        name="Palette format",
        description="Format of the stored palette",
        items=(
            ('INTENSITYA8', "IntensityA8", "8 bit grayscale color pixel."),
            ('RGB565', "Rgb565", "16 bit RGB color pixel"),
            ('RGB5A3', "Rgb5a3", "A 16 bit pixel, which is either 15 bits RGB or 15 bits ARGB")
        ),
        default='RGB5A3'
    )

def _get_pv_has_mipmaps(saio_texture_pv):
    return saio_texture_pv.mipmap_mode != 'NONE'

def _set_pv_has_mipmaps(saio_texture_pv, value: bool):
    saio_texture_pv.mipmap_mode = 'INCLUDE' if value else 'NONE'

PV_MIPMAP_FORMATS = {
    'SQUARETWIDDLED',
    'VQ',
    'SMALLVQ',
    'INDEX4',
    'INDEX8',
}

class SAIO_Texture_PV(bpy.types.PropertyGroup):

    data_format: EnumProperty(
        name="Data format",
        description="How pixels should be arranged in the encoded texture",
        items=(
            ('RECTANGLE', "Rectangle", "Row by row arrangement of any size."),
            ('RECTANGLETWIDDLED', "Rectangle Twiddled", "Encodes pixels with the Twiddle (Z-order) pattern that is not limited to a square shape."),
            ('STRIDE', "Stride", "Same as Rectangle but with a more limited dimension range."),
            ('SQUARETWIDDLED', "Square Twiddled", "Encodes pixels with the Twiddle (Z-order) pattern."),
            ('VQ', "Vq", "Encodes pixels into reused 2x2 blocks using vector quantization."),
            ('SMALLVQ', "Small Vq", "Encodes pixels into reused 2x2 blocks using vector quantization. Smaller textures have less blocks available."),
            ('INDEX4', "Index 4", "Pixels store a palette index instead of the colors directly. Each pixel takes 4 bits."),
            ('INDEX8', "Index 8", "Pixels store a palette index instead of the colors directly. Each pixel takes 8 bits."),
        ),
        default='RECTANGLE'
    )

    pixel_format: EnumProperty(
        name="Pixel format",
        description="How individual pixels should be encoded",
        items=(
            ('ARGB1555', "ARGB1555", "16 bit color pixels; 1 Alpha bit and 5 for each color."),
            ('RGB565', "RGB565", "16 bit RGB pixel."),
            ('ARGB4', "ARGB4", "16 bit color pixels, where each channel takes 4 bits."),
            ('YUV422', "YUV422", "Luma + double chroma color encoding. 4 bytes store 2 pixels, where where both pixels share the double chroma."),
            ('BUMP', "Bump", "A format closely related to modern normal maps. It stores a direction using 2 angles, instead of storing 3 component vector directly."),
            ('ARGB8', "ARGB8", "32 bit color pixels, where each channel takes a byte."),
            ('RGB24', "RGB24", "Luma + chroma color encoding.")
        ),
        default='ARGB1555'
    )

    mipmap_mode: EnumProperty(
        name="Mipmap mode",
        description="How mipmaps should be exported",
        items=(
            ('NONE', "None", "No mipmaps"),
            ('INCLUDE', "Include", "Include mipmaps"),
            ('DMA', "Include (DMA)", "Mipmap mode exclusive to the data format \"Square Twiddled\","
            " where the 1x1 mipmap takes up as much space as a 2x2 mipmap regardless of pixel format")
        ),
        default='NONE'
    )

    has_mipmaps: BoolProperty(
        name="Has Mipmaps",
        description="Whether the texture has mipmaps",
        get=_get_pv_has_mipmaps,
        set=_set_pv_has_mipmaps
    )

class SAIO_Texture_PVX(bpy.types.PropertyGroup):
    # for image formatting, we use the PAK properties

    override_width: IntProperty(
        name="Override Width",
        description="Width of the texture to replace. Set 0 to not override",
        default=0,
        min=0
    )

    override_height: IntProperty(
        name="Override Height",
        description="Height of the texture to replace. Set 0 to not override",
        default=0,
        min=0
    )

class SAIO_Texture_PAK(bpy.types.PropertyGroup):
    image_format: EnumProperty(
        name="Image format",
        description="Format in which the image should be encoded",
        items=(
            ('DDSBC1', "DDS (BC1)", "DDS texture with RGB565 and 1 or 0 bits of alpha"),
            ('DDSBC2', "DDS (BC2)", "DDS texture with RGB565 and 4 bits of alpha"),
            ('DDSBC3', "DDS (BC3)", "DDS texture with RGB565 and 8 bits of alpha"),
            ('PNG', "PNG", ""),
            ('JPG', "JPG", ""),
            ('BMP', "BMP", "")
        ),
        default='DDSBC1'
    )

class SAIO_Texture(bpy.types.PropertyGroup):

    name: StringProperty(
        name="Slot name",
        description="The name of the slot",
        maxlen=0x28,
        default=""
    )

    global_index: IntProperty(
        name="Global Index",
        description="The global texture id in the texture file",
        default=0
    )

    image: PointerProperty(
        type=bpy.types.Image,
        name="Image"
    )

    texture_type: EnumProperty(
        name="Texture Type",
        description="Type of the texture; Determines whether a palette is generated among other things",
        items=(
            ('COLOR', "Color", "Texture is a color texture (RGBA)"),
            ('INDEX8', "8-Bit Index", "Texture is an 8-bit index texture (up to 256 palette colors)"),
            ('INDEX4', "4-Bit Index", "Texture is a 4-bit index texture (up to 16 palette colors)"),
        ),
        default='COLOR'
    )

    dither: BoolProperty(
        name="Dither",
        description="If the texture is a color texture, but gets exported as an index texture, apply dithering",
        default=True
    )

    gv: PointerProperty(type=SAIO_Texture_GV)
    pv: PointerProperty(type=SAIO_Texture_PV)
    pvx: PointerProperty(type=SAIO_Texture_PVX)
    pak: PointerProperty(type=SAIO_Texture_PAK)

    @property
    def index(self):
        path = repr(self)
        end = path.rfind(".")
        path = path[:end]
        textures = self.path_resolve(path)

        for index, texture in enumerate(textures):
            if texture == self:
                return index

        raise SAIOException("Texture has no index")

    @classmethod
    def register(cls):
        pass

class SAIO_TextureList(BaseList):

    archive_format: EnumProperty(
        name="Archive format",
        description="The format of archive that the list should be exported as",
        items=(
            ('PAK', "PAK", "Generic file archive used by SEGA games"),
            ('GVM', "GVM", "Texture archvie designed for the gamecube"),
            ('PVM', "PVM", "Texture archive designed for the dreamcast"),
            ('PVMX', "PVMX", "Custom texture archive designed for SA1 modding")
        ),
        default='PAK'
    )

    palette_handling: EnumProperty(
        name="Palette handling",
        description="How to handle generated, external palettes",
        items=(
            ('EXPORT', "Export", "Export the generated palettes to files next to the archive"),
            ('EMBED', "Embed", "Embed the generated palettes inside the archive"),
            ('IGNORE', "Ignore", "Do nothing with the generated palettes"),
        ),
        default='EXPORT'
    )

    compress: BoolProperty(
        name="Compress",
        description="Whether the archive should be compressed to a .prs file when exporting",
        default=True
    )

    elements: CollectionProperty(
        type=SAIO_Texture,
        name="Texture List",
        description="The textures used by sonic adventure"
    )

    @classmethod
    def _get_index_comparator(cls, value):
        if isinstance(value, str):
            return lambda x: x.name == value
        elif isinstance(value, SAIO_Texture):
            return lambda x: x == value
        elif isinstance(value, bpy.types.Image):
            return lambda x: x.image == value
        raise NotImplementedError()

    def _on_created(self, value, **args):
        # getting next usable global id
        ids = [t.global_index for t in self]
        ids.sort(key=lambda x: x)

        global_index = len(self)
        for i, index in enumerate(ids):
            if i != index:
                global_index = i
                break
        value.global_index = global_index

        if "image" in args:
            value.image = args["image"]

        if "name" in args:
            value.name = args["name"]
        elif value.image is not None:
            value.name = os.path.splitext(value.image.name)[0]
        else:
            value.name = "Texture"

    def _on_clear(self):
        for t in self:
            if t.image is not None:
                t.image.use_fake_user = False

    def autoname(self):
        for tex in self:
            if tex.image is not None:
                tex.name = os.path.splitext(tex.image.name)[0]
            else:
                tex.name = "Texture"

    @ classmethod
    def register(cls):
        bpy.types.World.saio_texture_list = PointerProperty(
            type=cls,
            name="SAIO Texture Lists"
        )

        bpy.types.Object.saio_texture_world = PointerProperty(
            type=bpy.types.World,
            name="SAIO Texture World",
            description="Used as texture list storage"
        )
