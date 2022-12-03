import bpy
from bpy.props import (
    BoolProperty,
    PointerProperty
)

from . import (
    material,
    land_entry,
    node,
    mesh,
    panel_properties
)


class SAIO_QuickEdit(bpy.types.PropertyGroup):

    panels: PointerProperty(
        type=panel_properties.SAIO_PanelSettings,
        name="Panel properties"
    )

    # === To-Apply Material properties ===

    material_properties: PointerProperty(
        type=material.SAIO_Material,
        name="Material properties"
    )

    use_material_edit: BoolProperty(
        name="Activate Quick Material Edit",
        description=(
            "When active, the Buttons will use"
             " and apply the material properties"
        ),
        default=False
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

    # === To-Apply Landentry properties ===

    land_entry_properties: PointerProperty(
        type=land_entry.SAIO_LandEntry,
        name="Land Entry properties"
    )

    use_land_entry_edit: BoolProperty(
        name="Activate Quick LandEntry Edit",
        description=(
            "When active, the Buttons will use"
            " and apply the landtable properties"
        ),
        default=False
    )

    apply_blockbit: BoolProperty(
        name="Apply Blockbit",
        description=(
            "Sets the Blockbit of all selected"
            " objects when pressing 'Set'"
        ),
        default=False
    )

    # === Node ===

    use_node_edit: BoolProperty(
        name="Activate Quick Node Edit",
        description=(
            "When active, the Buttons will use"
            " and apply the node properties"
        ),
        default=False
    )

    node_properties: PointerProperty(
        type=node.SAIO_Node,
        name="Node properties"
    )

    # === Mesh ===

    use_mesh_edit: BoolProperty(
        name="Activate Quick Mesh Edit",
        description=(
            "When active, the Buttons will use"
            " and apply the mesh properties"
        ),
        default=False
    )

    mesh_properties: PointerProperty(
        type=mesh.SAIO_Mesh,
        name="Mesh Properties"
    )

    @classmethod
    def register(cls):
        pass
