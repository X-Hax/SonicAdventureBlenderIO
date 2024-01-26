from ..utility.enum_lut import (
    SURFACE_ATTRIBUTES,
    BLEND_MODE,
    FILTER_MODE,
    GC_TEXCOORD_ID,
    GC_TEXCOORD_TYPE,
    GC_TEXCOORD_SOURCE,
    GC_TEXCOORD_MATRIX,
    ATTACH_FORMAT,
    MODEL_FORMAT,
    EVENT_TYPE
)
from ..dotnet import SAIO_NET, SA3D_Modeling, SA3D_SA2Event


def to_node_attributes(node_properties):
    return SAIO_NET.FLAGS.ComposeNodeAttributes(
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
    return SAIO_NET.FLAGS.ComposeEventEntryAttributes(
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
    names = [
        name_to
        for name_from, name_to in SURFACE_ATTRIBUTES.items()
        if name_from.startswith("sf_")
        and getattr(saio_land_entry, name_from)]

    return SAIO_NET.FLAGS.ComposeSurfaceAttributes(names)


def to_blend_mode(blend_mode: str):
    return getattr(SA3D_Modeling.BLEND_MODE, BLEND_MODE[blend_mode])


def to_filter_mode(filter_mode: str):
    return getattr(SA3D_Modeling.FILTER_MODE, FILTER_MODE[filter_mode])


def to_texcoord_id(tex_coord_id: str):
    return getattr(SA3D_Modeling.GC_TEXCOORD_ID, GC_TEXCOORD_ID[tex_coord_id])


def to_texcoord_type(tex_gen_type: str):
    return getattr(SA3D_Modeling.GC_TEXCOORD_TYPE, GC_TEXCOORD_TYPE[tex_gen_type])


def to_texcoord_matrix(tex_gen_matrix: str):
    return getattr(SA3D_Modeling.GC_TEXCOORD_MATRIX, GC_TEXCOORD_MATRIX[tex_gen_matrix])


def to_texcoord_source(texgen_source: str):
    return getattr(SA3D_Modeling.GC_TEXCOORD_SOURCE, GC_TEXCOORD_SOURCE[texgen_source])


def to_attach_format(attach_format: str):
    return getattr(SA3D_Modeling.ATTACH_FORMAT, ATTACH_FORMAT[attach_format])


def to_model_format(model_format: str):
    return getattr(SA3D_Modeling.MODEL_FORMAT, MODEL_FORMAT[model_format])

def to_event_type(event_type: str):
    return getattr(SA3D_SA2Event.EVENT_TYPE, EVENT_TYPE[event_type])
