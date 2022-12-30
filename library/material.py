import bpy
from . import enum
from ..register.property_groups import SAIO_Material


def _get_texture_id(
        context: bpy.types.Context,
        material: bpy.types.Material):

    try:
        texture_node: bpy.types.ShaderNodeTexImage \
            = material.node_tree.nodes["SAIO Texture"]

        if texture_node.image is not None:
            textures = context.scene.saio_scene.texture_list.textures

            for i, tex in enumerate(textures):
                if tex.image == texture_node.image:
                    return i

    except Exception:
        pass

    return material.saio_material.texture_id


def default_material_struct():
    from SATools.SAModel.Blender import MaterialStruct, Flags
    from SATools.SAModel.ModelData import BlendMode, FilterMode
    from SATools.SAModel.ModelData.GC import (
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
        context: bpy.types.Context,
        material: bpy.types.Material):

    if material is None:
        return default_material_struct()

    props: SAIO_Material = material.saio_material

    dc = props.diffuse
    sc = props.specular
    ac = props.ambient

    texture_id = _get_texture_id(context, material)

    from SATools.SAModel.Blender import Flags

    material_attributes = Flags.ComposeMaterialAttributes(
        props.flat_shading,
        props.ignore_ambient,
        props.ignore_diffuse,
        props.ignore_specular,
        props.use_texture,
        props.use_environment
    )

    filter_mode = enum.to_filter_mode(props.texture_filtering)
    source_blend_mode = enum.to_blend_mode(props.source_alpha)
    destination_blend_mode = enum.to_blend_mode(
        props.destination_alpha)

    tex_coord_id = enum.to_tex_coord_id(props.texgen_coord_id)
    tex_gen_type = enum.to_tex_gen_type(props.texgen_type)
    tex_gen_source = enum.to_tex_gen_source(props)
    tex_gen_matrix = enum.to_tex_gen_matrix(props.texgen_matrix_id)

    from SATools.SAModel.Blender import MaterialStruct
    return MaterialStruct(
        dc[0], dc[1], dc[2], dc[3],
        sc[0], sc[1], sc[2], sc[3],
        props.specular_exponent,
        ac[0], ac[1], ac[2], ac[3],
        material_attributes,
        props.use_alpha,
        props.culling,
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
