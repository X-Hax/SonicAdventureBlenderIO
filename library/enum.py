BLEND_MODE = {
    'ZERO': "Zero",
    "Zero": 'ZERO',

    'ONE': "One",
    "One": 'ONE',

    'OTHER': "Other",
    "Other": 'OTHER',

    'INV_OTHER': "OtherInverted",
    "OtherInverted": 'INV_OTHER',

    'SRC': "SrcAlpha",
    "SrcAlpha": 'SRC',

    'INV_SRC': "SrcAlphaInverted",
    "SrcAlphaInverted": 'INV_SRC',

    'DST': "DstAlpha",
    "DstAlpha": 'DST',

    'INV_DST': "DstAlphaInverted",
    "DstAlphaInverted": 'INV_DST',
}

FILTER_MODE = {
    'POINT': "PointSampled",
    "PointSampled": 'POINT',

    'BILINEAR': "Bilinear",
    "Bilinear": 'BILINEAR',

    'TRILINEAR': "Trilinear",
    "Trilinear": 'TRILINEAR',

    'BLEND': "Blend",
    "Blend": 'BLEND',

}

TEX_COORD_ID = {
    'TEXCOORD0': "TexCoord0",
    "TexCoord0": 'TEXCOORD0',

    'TEXCOORD1': "TexCoord1",
    "TexCoord1": 'TEXCOORD1',

    'TEXCOORD2': "TexCoord2",
    "TexCoord2": 'TEXCOORD2',

    'TEXCOORD3': "TexCoord3",
    "TexCoord3": 'TEXCOORD3',

    'TEXCOORD4': "TexCoord4",
    "TexCoord4": 'TEXCOORD4',

    'TEXCOORD5': "TexCoord5",
    "TexCoord5": 'TEXCOORD5',

    'TEXCOORD6': "TexCoord6",
    "TexCoord6": 'TEXCOORD6',

    'TEXCOORD7': "TexCoord7",
    "TexCoord7": 'TEXCOORD7',

    'TEXCOORDMAX': "TexCoordMax",
    "TexCoordMax": 'TEXCOORDMAX',

    'TEXCOORDNULL': "TexCoordNull",
    "TexCoordNull": 'TEXCOORDNULL',

}

TEX_GEN_TYPE = {
    'MATRIX3X4': "Matrix3x4",
    "Matrix3x4": 'MATRIX3X4',

    'MATRIX2X4': "Matrix2x4",
    "Matrix2x4": 'MATRIX2X4',

    'BITMAP0': "Bitmap0",
    "Bitmap0": 'BITMAP0',

    'BITMAP1': "Bitmap1",
    "Bitmap1": 'BITMAP1',

    'BITMAP2': "Bitmap2",
    "Bitmap2": 'BITMAP2',

    'BITMAP3': "Bitmap3",
    "Bitmap3": 'BITMAP3',

    'BITMAP4': "Bitmap4",
    "Bitmap4": 'BITMAP4',

    'BITMAP5': "Bitmap5",
    "Bitmap5": 'BITMAP5',

    'BITMAP6': "Bitmap6",
    "Bitmap6": 'BITMAP6',

    'BITMAP7': "Bitmap7",
    "Bitmap7": 'BITMAP7',

    'SRTG': "SRTG",
}

TEX_GEN_SOURCE = {
    'POSITION': "Position",
    "Position": 'POSITION',

    'NORMAL': "Normal",
    "Normal": 'NORMAL',

    'BINORMAL': "Binormal",
    "Binormal": 'BINORMAL',

    'TANGENT': "Tangent",
    "Tangent": 'TANGENT',

    'TEX0': "Tex0",
    "Tex0": 'TEX0',

    'TEX1': "Tex1",
    "Tex1": 'TEX1',

    'TEX2': "Tex2",
    "Tex2": 'TEX2',

    'TEX3': "Tex3",
    "Tex3": 'TEX3',

    'TEX4': "Tex4",
    "Tex4": 'TEX4',

    'TEX5': "Tex5",
    "Tex5": 'TEX5',

    'TEX6': "Tex6",
    "Tex6": 'TEX6',

    'TEX7': "Tex7",
    "Tex7": 'TEX7',

    'TEXCOORD0': "TexCoord0",
    "TexCoord0": 'TEXCOORD0',

    'TEXCOORD1': "TexCoord1",
    "TexCoord1": 'TEXCOORD1',

    'TEXCOORD2': "TexCoord2",
    "TexCoord2": 'TEXCOORD2',

    'TEXCOORD3': "TexCoord3",
    "TexCoord3": 'TEXCOORD3',

    'TEXCOORD4': "TexCoord4",
    "TexCoord4": 'TEXCOORD4',

    'TEXCOORD5': "TexCoord5",
    "TexCoord5": 'TEXCOORD5',

    'TEXCOORD6': "TexCoord6",
    "TexCoord6": 'TEXCOORD6',

    'COLOR0': "Color0",
    "Color0": 'COLOR0',

    'COLOR1': "Color1",
    "Color1": 'COLOR1',

}

TEX_GEN_MATRIX = {
    'MATRIX0': "Matrix0",
    "Matrix0": 'MATRIX0',

    'MATRIX1': "Matrix1",
    "Matrix1": 'MATRIX1',

    'MATRIX2': "Matrix2",
    "Matrix2": 'MATRIX2',

    'MATRIX3': "Matrix3",
    "Matrix3": 'MATRIX3',

    'MATRIX4': "Matrix4",
    "Matrix4": 'MATRIX4',

    'MATRIX5': "Matrix5",
    "Matrix5": 'MATRIX5',

    'MATRIX6': "Matrix6",
    "Matrix6": 'MATRIX6',

    'MATRIX7': "Matrix7",
    "Matrix7": 'MATRIX7',

    'MATRIX8': "Matrix8",
    "Matrix8": 'MATRIX8',

    'MATRIX9': "Matrix9",
    "Matrix9": 'MATRIX9',

    'IDENTITY': "Identity",
    "Identity": 'IDENTITY',

}

ATTACH_FORMAT = {
    'BUF': 'BUFFER',
    'BUFFER': 'BUF',

    'SA1': "BASIC",
    "BASIC": 'SA1',

    'SA2': "CHUNK",
    "CHUNK": 'SA2',

    'SA2B': "GC",
    "GC": 'SA2B',

}


def to_blend_mode(blend_mode: str):
    from SATools.SAModel.ModelData import BlendMode
    return getattr(BlendMode, BLEND_MODE[blend_mode])


def from_blend_mode(enum):
    return BLEND_MODE[enum.ToString()]


def to_filter_mode(filter_mode: str):
    from SATools.SAModel.ModelData import FilterMode
    return getattr(FilterMode, FILTER_MODE[filter_mode])


def from_filter_mode(enum):
    return FILTER_MODE[enum.ToString()]


def to_tex_coord_id(tex_coord_id: str):
    from SATools.SAModel.ModelData.GC import TexCoordID
    return getattr(TexCoordID, TEX_COORD_ID[tex_coord_id])


def from_tex_coord_id(enum):
    return TEX_COORD_ID[enum.ToString()]


def to_tex_gen_type(tex_gen_type: str):
    from SATools.SAModel.ModelData.GC import TexGenType
    return getattr(TexGenType, TEX_GEN_TYPE[tex_gen_type])


def from_tex_gen_type(enum):
    return TEX_GEN_TYPE[enum.ToString()]


def to_tex_gen_matrix(tex_gen_matrix: str):
    from SATools.SAModel.ModelData.GC import TexGenMatrix
    return getattr(TexGenMatrix, TEX_GEN_MATRIX[tex_gen_matrix])


def from_tex_gen_matrix(enum):
    return TEX_GEN_MATRIX[enum.ToString()]


def to_tex_gen_source(saio_material):
    type = saio_material.texgen_type[0]
    if type == 'M':
        name = saio_material.texgen_source_matrix
    elif type == 'B':
        name = saio_material.texgen_source_bitmap
    else:
        name = saio_material.texgen_source_srtg

    from SATools.SAModel.ModelData.GC import TexGenSrc
    return getattr(TexGenSrc, TEX_GEN_SOURCE[name])


def from_tex_gen_source(enum, saio_material):
    value = TEX_GEN_SOURCE[enum.ToString()]

    if len(value) == 4:  # TEX%
        saio_material.texgen_source_bitmap = value
    elif value.startswith("COLOR"):
        saio_material.texgen_source_srtg = value
    else:
        saio_material.texgen_source_matrix = value


def to_attach_format(format):
    from SATools.SAModel.ModelData import AttachFormat
    return getattr(AttachFormat, ATTACH_FORMAT[format])


def from_attach_format(enum):
    return ATTACH_FORMAT[enum.ToString()]
