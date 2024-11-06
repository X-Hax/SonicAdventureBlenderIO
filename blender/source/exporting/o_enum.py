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
    EVENT_TYPE,
    AUTO_NODE_ATTRIBUTE_MODE
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
        node_properties.no_morph,
        node_properties.clip,
        node_properties.modifier,
        node_properties.use_quaternion_rotation,
        node_properties.cache_rotation,
        node_properties.apply_cached_rotation,
        node_properties.envelope
    )


def to_evententry_attributes(evententry_properties):
    return SAIO_NET.FLAGS.ComposeEventEntryAttributes(
        evententry_properties.has_environment,
        evententry_properties.no_fog_and_easy_draw,
        evententry_properties.light1,
        evententry_properties.light2,
        evententry_properties.light3,
        evententry_properties.light4,
        evententry_properties.modifier_volume,
        evententry_properties.reflection,
        evententry_properties.blare,
        evententry_properties.use_simple
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


def to_auto_node_attribute_mode(auto_node_attribute_mode: str):
    return getattr(SAIO_NET.AUTO_NODE_ATTRIBUTES, AUTO_NODE_ATTRIBUTE_MODE[auto_node_attribute_mode])