from ..utility.enum_lut import (
    SURFACE_ATTRIBUTES,
    BLEND_MODE,
    FILTER_MODE,
    GC_TEXCOORD_ID,
    GC_TEXCOORD_TYPE,
    GC_TEXCOORD_SOURCE,
    GC_TEXCOORD_MATRIX,
    ATTACH_FORMAT,
    MODEL_FORMAT
)
from ..dotnet import SAIO_NET


def from_node_attributes(node_properties, attributes: any):
    node_properties.ignore_position, \
        node_properties.ignore_rotation, \
        node_properties.ignore_scale, \
        node_properties.skip_draw, \
        node_properties.skip_children, \
        node_properties.rotate_zyx, \
        node_properties.no_animate, \
        node_properties.no_morph, \
        node_properties.clip, \
        node_properties.modifier, \
        node_properties.use_quaternion_rotation, \
        node_properties.cache_rotation, \
        node_properties.apply_cached_rotation, \
        node_properties.envelope, \
        = SAIO_NET.FLAGS.DecomposeNodeAttributes(attributes)


def from_evententry_attributes(evententry_properties, attributes: any):
    evententry_properties.has_environment, \
        evententry_properties.no_fog_and_easy_draw, \
        evententry_properties.light1, \
        evententry_properties.light2, \
        evententry_properties.light3, \
        evententry_properties.light4, \
        evententry_properties.modifier_volume, \
        evententry_properties.reflection, \
        evententry_properties.blare, \
        evententry_properties.use_simple \
        = SAIO_NET.FLAGS.DecomposeEventEntryAttributes(attributes)


def from_surface_attributes(attributes: any, saio_land_entry):
    mapping = SAIO_NET.FLAGS.DecomposeSurfaceAttributes(attributes)

    for value in mapping:
        attribute = SURFACE_ATTRIBUTES[value]
        if attribute is not None:
            setattr(saio_land_entry, attribute, True)


def from_blend_mode(enum: any):
    return BLEND_MODE[enum.ToString()]


def from_filter_mode(enum: any):
    return FILTER_MODE[enum.ToString()]


def from_tex_coord_id(enum: any):
    return GC_TEXCOORD_ID[enum.ToString()]


def from_tex_gen_type(enum: any):
    return GC_TEXCOORD_TYPE[enum.ToString()]


def from_tex_gen_matrix(enum: any):
    return GC_TEXCOORD_MATRIX[enum.ToString()]


def from_tex_gen_source(enum: any):
    return GC_TEXCOORD_SOURCE[enum.ToString()]


def from_attach_format(enum: any):
    return ATTACH_FORMAT[enum.ToString()]


def from_landtable_format(enum: any):
    return MODEL_FORMAT[enum.ToString()]
