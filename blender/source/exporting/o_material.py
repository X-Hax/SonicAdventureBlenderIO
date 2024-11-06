import bpy

from ..register.property_groups.material_properties import SAIO_Material
from ..utility.texture_manager import TexlistManager
from ..dotnet import SA3D_Modeling

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
    return SA3D_Modeling.BUFFER_MATERIAL.DefaultValues


def convert_material_to_struct(
        material: bpy.types.Material | None,
        texlist_manager: TexlistManager):

    if material is None:
        return default_material_struct()

    props: SAIO_Material = material.saio_material

    dc = props.diffuse
    sc = props.specular
    ac = props.ambient

    texture_id = _get_texture_id(material, texlist_manager)

    from . import o_enum

    result = SA3D_Modeling.BUFFER_MATERIAL()

    result.Diffuse = SA3D_Modeling.COLOR(dc[0], dc[1], dc[2], dc[3])
    result.Specular = SA3D_Modeling.COLOR(sc[0], sc[1], sc[2], sc[3])
    result.SpecularExponent = props.specular_exponent
    result.Ambient = SA3D_Modeling.COLOR(ac[0], ac[1], ac[2], ac[3])
    result.TextureIndex = texture_id
    result.MipmapDistanceMultiplier = props.mipmap_distance_multiplier

    result.TextureFiltering = o_enum.to_filter_mode(props.texture_filtering)
    result.SourceBlendMode = o_enum.to_blend_mode(props.source_alpha)
    result.DestinationBlendmode = o_enum.to_blend_mode(
        props.destination_alpha)

    result.Flat = props.flat_shading
    result.NoLighting = props.ignore_diffuse
    result.NoAmbient = props.ignore_ambient
    result.NoSpecular = props.ignore_specular
    result.UseTexture = props.use_texture
    result.NormalMapping = props.use_environment
    result.ClampU = props.clamp_u
    result.ClampV = props.clamp_v
    result.MirrorU = props.mirror_u
    result.MirrorV = props.mirror_v
    result.UseAlpha = props.use_alpha
    result.BackfaceCulling = not props.double_sided
    result.NoAlphaTest = props.no_alpha_test
    result.AnisotropicFiltering = props.anisotropic_filtering

    result.GCShadowStencil = props.shadow_stencil
    result.GCTexCoordID = o_enum.to_texcoord_id(props.texgen_coord_id)
    result.GCTexCoordType = o_enum.to_texcoord_type(props.texgen_type)
    result.GCTexCoordSource = o_enum.to_texcoord_source(props.texgen_source)
    result.GCMatrixID = o_enum.to_texcoord_matrix(props.texgen_matrix_id)

    return result
