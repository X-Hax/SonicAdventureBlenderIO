import bpy
from bpy.props import (
    BoolProperty,
    PointerProperty
)

from .material_properties import SAIO_Material
from .panel_properties import SAIO_PanelSettings


class SAIO_MaterialMassEdit(bpy.types.PropertyGroup):

    panels: PointerProperty(
        type=SAIO_PanelSettings,
        name="Panel properties"
    )

    material_properties: PointerProperty(
        type=SAIO_Material,
        name="Material properties"
    )

    apply_diffuse: BoolProperty(
        name="Apply diffuse",
        description=(
            "Sets the diffuse color of all selected"
            " materials when pressing 'Set'"
        ),
        default=False
    )

    apply_specular: BoolProperty(
        name="Apply specular",
        description=(
            "Sets the specular color of all selected"
            " materials when pressing 'Set'"
        ),
        default=False
    )

    apply_ambient: BoolProperty(
        name="Apply ambient",
        description=(
            "Sets the ambient color of all selected"
            " materials when pressing 'Set'"
        ),
        default=False
    )

    apply_specularity: BoolProperty(
        name="Apply specularity",
        description=(
            "Sets the specularity of all selected"
            " materials when pressing 'Set'"
        ),
        default=False
    )

    apply_texture_id: BoolProperty(
        name="Apply texture ID",
        description=(
            "Sets the texture id of all selected"
            " materials when pressing 'Set'"
        ),
        default=False
    )

    apply_filter: BoolProperty(
        name="Apply filter type",
        description=(
            "Sets the filtering of all selected"
            " materials when pressing 'Set'"
        ),
        default=False
    )

    apply_mipmap_distance_multiplier: BoolProperty(
        name="Apply mipmap distance multiplier",
        description=(
            "Sets the mdm of all selected"
            " materials when pressing 'Set'"
        ),
        default=False
    )

    apply_source_alpha: BoolProperty(
        name="Apply source alpha",
        description=(
            "Sets the source alpha of all selected"
            " materials when pressing 'Set'"
        ),
        default=False
    )

    apply_destination_alpha: BoolProperty(
        name="Apply destination alpha",
        description=(
            "Sets the destination alpha of all selected"
            " materials when pressing 'Set'"
        ),
        default=False
    )

    apply_no_alpha_test: BoolProperty(
        name="Apply no alpha test",
        description=(
            "Sets the no alpha test property of all selected"
            " materials when pressing 'Set'"
        ),
        default=False
    )

    apply_shadow_stencil: BoolProperty(
        name="Apply shadow stencil",
        description=(
            "Sets the shadow stencil of all selected"
            " materials when pressing 'Set'"
        ),
        default=False
    )

    apply_texgen_coord_id: BoolProperty(
        name="Apply Texcoord ID",
        description=(
            "Sets the texgen coord id of all selected"
            " materials when pressing 'Set'"
        ),
        default=False
    )

    apply_texgen_type: BoolProperty(
        name="Apply Type",
        description=(
            "Sets the texgen type of all selected"
            " materials when pressing 'Set'"
        ),
        default=False
    )

    apply_texgen_matrix_id: BoolProperty(
        name="Apply Matrix ID",
        description=(
            "Sets the texgen matrix id of all selected"
            " materials when pressing 'Set'"
        ),
        default=False
    )

    apply_texgen_source: BoolProperty(
        name="Apply Source",
        description=(
            "Sets the texgen source of all selected"
            " materials when pressing 'Set'"
        ),
        default=False
    )
