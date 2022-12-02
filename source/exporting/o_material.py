import bpy

from ..register.property_groups.material_properties import SAIO_Material
from ..utility.texture_manager import TexlistManager


def _get_texture_id(
        material: bpy.types.Material,
        texlist_manager: TexlistManager):

    try:
        texture_node: bpy.types.ShaderNodeTexImage \
            = material.node_tree.nodes["SAIO Texture"]

        if texture_node.image is not None:
            texlist = texlist_manager.get_material_texlist(material)

            for i, tex in enumerate(texlist.textures):
                if tex.image == texture_node.image:
                    return i

    except Exception:
        pass

    return material.saio_material.texture_id


def default_material_struct():
    from SA3D.Modeling.Blender import MaterialStruct, Flags
    from SA3D.Modeling.ModelData import BlendMode, FilterMode
    from SA3D.Modeling.ModelData.GC import (
        TexCoordID, TexGenType, TexGenSrc, TexGenMatrix)

    material_attributes = Flags.ComposeMaterialAttributes(
        False, False, False, False, False, False)

    return MaterialStruct(
        1, 1, 1, 1,  # white
        1, 1, 1, 1,  # white
        3,
        0.3, 0.3, 0.3, 1,  # dark gray
        material_attributes,
        False,
        False,
        BlendMode.SrcAlpha,
        BlendMode.SrcAlphaInverted,
        0,
        FilterMode.Bilinear,
        False,
        0,
        False, False,
        False, False,
        0,
        TexCoordID.TexCoord0,
        TexGenType.Matrix2x4,
        TexGenSrc.TexCoord0,
        TexGenMatrix.Matrix0
    )


def convert_material_to_struct(
        material: bpy.types.Material,
        texlist_manager: TexlistManager):

    from . import o_enum

    if material is None:
        return default_material_struct()

    props: SAIO_Material = material.saio_material

    dc = props.diffuse
    sc = props.specular
    ac = props.ambient

    texture_id = _get_texture_id(material, texlist_manager)

    from SA3D.Modeling.Blender import Flags

    material_attributes = Flags.ComposeMaterialAttributes(
        props.flat_shading,
        props.ignore_ambient,
        props.ignore_diffuse,
        props.ignore_specular,
        props.use_texture,
        props.use_environment
    )

    filter_mode = o_enum.to_filter_mode(props.texture_filtering)
    source_blend_mode = o_enum.to_blend_mode(props.source_alpha)
    destination_blend_mode = o_enum.to_blend_mode(
        props.destination_alpha)

    tex_coord_id = o_enum.to_tex_coord_id(props.texgen_coord_id)
    tex_gen_type = o_enum.to_tex_gen_type(props.texgen_type)
    tex_gen_source = o_enum.to_tex_gen_source(props.texgen_source)
    tex_gen_matrix = o_enum.to_tex_gen_matrix(props.texgen_matrix_id)

    from SA3D.Modeling.Blender import MaterialStruct
    return MaterialStruct(
        dc[0], dc[1], dc[2], dc[3],
        sc[0], sc[1], sc[2], sc[3],
        props.specular_exponent,
        ac[0], ac[1], ac[2], ac[3],
        material_attributes,
        props.use_alpha,
        not props.double_sided,
        source_blend_mode,
        destination_blend_mode,
        texture_id,
        filter_mode,
        props.anisotropic_filtering,
        props.mipmap_distance_multiplier,
        props.clamp_u, props.mirror_u,
        props.clamp_v, props.mirror_v,
        props.shadow_stencil,
        tex_coord_id,
        tex_gen_type,
        tex_gen_source,
        tex_gen_matrix
    )
