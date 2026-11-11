CHUNK_VERTEX_TYPE = [
    'BLANK4',
    'NORMAL4',
    'BLANK',
    'DIFFUSE',
    'USER_ATTR',
    'BLANK',
    'DIFF_SPEC_5',
    'DIFF_SPEC_4',
    'INTENSITY',
    'NORMAL',
    'NORMAL_DIFFUSE',
    'NORMAL_USER_ATTR',
    'NORMAL',
    'NORMAL_DIFF_SPEC_5',
    'NORMAL_DIFF_SPEC_4',
    'NORMAL_INTENSITY',
    'NORMAL32',
    'NORMAL32_DIFFUSE',
    'NORMAL32_USER_ATTR',
    'DIFF_SPEC',
    'DIFFUSE'
]

TEXTURE_FILTER_MODE = [
    'NEAREST',
    'BILINEAR',
    'TRILINEAR',
    'TRILINEAR'
]

ALPHA_MODE = [
    'OPAQUE',
    'TRANSPARENT',
    'FORCE_CLIP_ON',
    'FORCE_CLIP_OFF',
]

BLEND_MODE = [
    'ZERO',
    'ONE',
    'OTHER',
    'INV_OTHER',
    'SRC',
    'INV_SRC',
    'DST',
    'INV_DST',
]

GINJA_COLOR_CHANNEL = [
    'COLOR0',
    'COLOR1',
    'ALPHA0',
    'ALPHA1',
    'COLOR0A0',
    'COLOR1A1',
    'COLORZERO',
    'ALPHABUMP',
    'ALPHABUMPN',
]

GINJA_TEXGEN_TYPE = [
    'MATRIX3X4',
    'MATRIX2X4',
    'BUMP0',
    'BUMP1',
    'BUMP2',
    'BUMP3',
    'BUMP4',
    'BUMP5',
    'BUMP6',
    'BUMP7',
    'SRTG',
]

GINJA_TEXGEN_SOURCE = [
    'POSITION',
    'NORMAL',
    'BINORMAL',
    'TANGENT',
    'TEXCOORD0',
    'TEXCOORD1',
    'TEXCOORD2',
    'TEXCOORD3',
    'TEXCOORD4',
    'TEXCOORD5',
    'TEXCOORD6',
    'TEXCOORD7',
    'BUMPTEXCOORD0',
    'BUMPTEXCOORD1',
    'BUMPTEXCOORD2',
    'BUMPTEXCOORD3',
    'BUMPTEXCOORD4',
    'BUMPTEXCOORD5',
    'BUMPTEXCOORD6',
    'COLOR0',
    'COLOR1',
]

GINJA_MATRIX_ID = [
    'MATRIX0',
    'MATRIX1',
    'MATRIX2',
    'MATRIX3',
    'MATRIX4',
    'MATRIX5',
    'MATRIX6',
    'MATRIX7',
    'MATRIX8',
    'MATRIX9',
    'IDENTITY',
]

ARCHIVE_FORMAT = [
    'PAK',
    'GVM',
    'PVM',
    'PVMX',
]

TEXTURE_TYPE = [
    'COLOR',
    'INDEX8',
    'INDEX4',
]

GV_FORMAT = [ 
    'INTENSITY4',
    'INTENSITY8',
    'INTENSITYA4',
    'INTENSITYA8',
    'RGB565',
    'RGB5A3',
    'ARGB8',
    None,
    'INDEX4',
    'INDEX8',
    None,
    None,
    None,
    None,
    'DXT1',
]

GV_PALETTE_FORMAT = [
    'INTENSITYA8',
    'RGB565',
    'RGB5A3',
]

PV_PIXEL_FORMAT = [
    'ARGB1555',
    'RGB565',
    'ARGB4',
    'YUV422',
    'BUMP',
    'ARGB8',
    'RGB24',
]

PV_TEXTURE_DATA_FORMAT = [
    None,
    'SQUARETWIDDLED',
    'SQUARETWIDDLED',
    'VQ',
    'VQ',
    'INDEX4',
    'INDEX4',
    'INDEX8',
    'INDEX8',
    'RECTANGLE',
    None,
    'STRIDE',
    None,
    'RECTANGLETWIDDLED',
    None,
    None,
    'SMALLVQ',
    'SMALLVQ',
    'SQUARETWIDDLED',
]

PV_TEXTURE_DATA_FORMAT_MIPMAP = [
    None,
    'NONE',
    'INCLUDE',
    'NONE',
    'INCLUDE',
    'NONE',
    'INCLUDE',
    'NONE',
    'INCLUDE',
    'NONE',
    None,
    'NONE',
    None,
    'NONE',
    None,
    None,
    'NONE',
    'INCLUDE',
    'DMA',
]

IMAGE_FORMAT = [
    'DDSBC1',
    'DDSBC2',
    'DDSBC3',
    'PNG',
    'JPG',
    'BMP',
]