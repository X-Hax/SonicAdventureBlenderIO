from ..utility.enum_lut import *


def to_node_attributes(node_properties):
    from SA3D.Modeling.Blender import Flags
    return Flags.ComposeNodeAttributes(
        node_properties.ignore_position,
        node_properties.ignore_rotation,
        node_properties.ignore_scale,
        node_properties.skip_draw,
        node_properties.skip_children,
        node_properties.rotate_zyx,
        node_properties.no_animate,
        node_properties.no_morph
    )


def to_evententry_attributes(evententry_properties):
    from SA3D.Modeling.Blender import Flags
    return Flags.ComposeEventEntryAttributes(
        evententry_properties.unk0,
        evententry_properties.enable_lighting,
        evententry_properties.unk2,
        evententry_properties.disable_shadow_catching,
        evententry_properties.unk4,
        evententry_properties.unk5,
        evententry_properties.unk6,
        evententry_properties.reflection,
        evententry_properties.blare,
        evententry_properties.unk9
    )


def to_surface_attributes(saio_land_entry):
    from SA3D.Modeling.Blender import Flags

    names = [
        name_to
        for name_from, name_to in SURFACE_ATTRIBUTES.items()
        if name_from.startswith("sf_")
        and getattr(saio_land_entry, name_from)]

    return Flags.ComposeSurfaceAttributes(names)


def to_blend_mode(blend_mode: str):
    from SA3D.Modeling.ModelData import BlendMode
    return getattr(BlendMode, BLEND_MODE[blend_mode])


def to_filter_mode(filter_mode: str):
    from SA3D.Modeling.ModelData import FilterMode
    return getattr(FilterMode, FILTER_MODE[filter_mode])


def to_tex_coord_id(tex_coord_id: str):
    from SA3D.Modeling.ModelData.GC import TexCoordID
    return getattr(TexCoordID, TEX_COORD_ID[tex_coord_id])


def to_tex_gen_type(tex_gen_type: str):
    from SA3D.Modeling.ModelData.GC import TexGenType
    return getattr(TexGenType, TEX_GEN_TYPE[tex_gen_type])


def to_tex_gen_matrix(tex_gen_matrix: str):
    from SA3D.Modeling.ModelData.GC import TexGenMatrix
    return getattr(TexGenMatrix, TEX_GEN_MATRIX[tex_gen_matrix])


def to_tex_gen_source(texgen_source):
    from SA3D.Modeling.ModelData.GC import TexGenSrc
    return getattr(TexGenSrc, TEX_GEN_SOURCE[texgen_source])


def to_attach_format(format):
    from SA3D.Modeling.ModelData import AttachFormat
    return getattr(AttachFormat, ATTACH_FORMAT[format])


def to_model_format(format):
    from SA3D.Modeling.ObjectData import ModelFormat
    return getattr(ModelFormat, MODEL_FORMAT[format])

