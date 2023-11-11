from ..utility.enum_lut import *


def from_node_attributes(node_properties, attributes):
    from SA3D.Modeling.Blender import Flags
    node_properties.ignore_position, \
        node_properties.ignore_rotation, \
        node_properties.ignore_scale, \
        node_properties.skip_draw, \
        node_properties.skip_children, \
        node_properties.rotate_zyx, \
        node_properties.no_animate, \
        node_properties.no_morph \
        = Flags.DecomposeNodeAttributes(attributes)


def from_evententry_attributes(evententry_properties, attributes):
    from SA3D.Modeling.Blender import Flags
    evententry_properties.unk0, \
        evententry_properties.enable_lighting, \
        evententry_properties.unk2, \
        evententry_properties.disable_shadow_catching, \
        evententry_properties.unk4, \
        evententry_properties.unk5, \
        evententry_properties.unk6, \
        evententry_properties.reflection, \
        evententry_properties.blare, \
        evententry_properties.unk9 \
        = Flags.DecomposeEventEntryAttributes(attributes)


def from_surface_attributes(attributes, saio_land_entry):
    from SA3D.Modeling.Blender import Flags
    mapping = Flags.DecomposeSurfaceAttributes(attributes)

    for value in mapping:
        attribute = SURFACE_ATTRIBUTES[value]
        if attribute is not None:
            setattr(saio_land_entry, attribute, True)


def from_blend_mode(enum):
    return BLEND_MODE[enum.ToString()]


def from_filter_mode(enum):
    return FILTER_MODE[enum.ToString()]


def from_tex_coord_id(enum):
    return TEX_COORD_ID[enum.ToString()]


def from_tex_gen_type(enum):
    return TEX_GEN_TYPE[enum.ToString()]


def from_tex_gen_matrix(enum):
    return TEX_GEN_MATRIX[enum.ToString()]


def from_tex_gen_source(enum):
    return TEX_GEN_SOURCE[enum.ToString()]


def from_attach_format(enum):
    return ATTACH_FORMAT[enum.ToString()]


def from_landtable_format(enum):
    return MODEL_FORMAT[enum.ToString()]
