from ctypes import pointer
from typing import Callable
import bpy

from . import i_transform

from ..register.property_groups.mesh_properties import SAIO_Mesh
from ..register.property_groups.material_properties import SAIO_Material
from ..register.property_groups.ginja_material_properties import SAIO_Material_Ginja

from ..external import (
    SAIONET,
    enums, 
    CMeshConversionInfo, 
    CVertex, 
    CCorner, 
    CMaterial,
    CVector4
)
from ..utility import progress_console

class ConvertedMesh:

    mesh: bpy.types.Mesh
    mesh_info: CMeshConversionInfo
    has_weights: bool

    def __init__(
        self, 
        mesh: bpy.types.Mesh,
        mesh_info: CMeshConversionInfo,
        has_weights: bool):

        self.mesh = mesh
        self.mesh_info = mesh_info
        self.has_weights = has_weights

class MeshConverter:

    # Parameters
    _force_weights: bool

    # Session context
    _material_lookup: dict[int, bpy.types.Material]

    # Element context
    _container_name: str
    _node_names: list[str] | None
    _for_armature: bool

    _c_mesh_info: CMeshConversionInfo
    _c_vertices: list[CVertex]
    _c_materials: list[CMaterial]
    _c_triangle_sets: list[list[CCorner]]

    _mesh: bpy.types.Mesh

    def __init__(
        self,
        force_weights: bool):

        self._force_weights = force_weights
        self._material_lookup = dict()

    @property
    def force_weights(self):
        return self._force_weights
    

    def _prepare_c_data(self):
        self._c_vertices = [self._c_mesh_info.mesh.vertices[i] for i in range(self._c_mesh_info.mesh.vertices_size)]
        self._c_materials = [self._c_mesh_info.mesh.materials[i] for i in range(self._c_mesh_info.mesh.triangle_sets_size)]
        self._c_triangle_sets = []

        for i in range(self._c_mesh_info.mesh.triangle_sets_size):
            corners_pointer = self._c_mesh_info.mesh.triangle_sets[i]
            corners = [corners_pointer[j] for j in range(self._c_mesh_info.mesh.triangle_set_sizes[i])]
            self._c_triangle_sets.append(corners)

    def _convert_geometry(self):
        vertices = [i_transform.c_to_bpy_vector(x.position) for x in self._c_vertices]
        faces = []
        for triangle_set in self._c_triangle_sets:
            for i in range(0, len(triangle_set), 3):
                faces.append((
                    triangle_set[i].vertex_index,
                    triangle_set[i + 1].vertex_index,
                    triangle_set[i + 2].vertex_index
                ))

        self._mesh.from_pydata(vertices, [], faces, shade_flat=not self._c_mesh_info.has_normals)

    def _convert_material(self, material: CMaterial, name: str):
        result = bpy.data.materials.new(name)
        saio_mat: SAIO_Material = result.saio_material

        saio_mat.rendering_model = 'FLAT' if material.flat_shading else 'SMOOTH'
        saio_mat.double_sided = material.double_sided

        saio_mat.alpha_mode = enums.ALPHA_MODE[material.alpha_mode]
        saio_mat.source_blendmode = enums.BLEND_MODE[material.source_blend_mode]
        saio_mat.destination_blendmode = enums.BLEND_MODE[material.destination_blend_mode]

        saio_mat.ignore_lighting = material.ignore_lighting
        saio_mat.ignore_ambient = material.ignore_ambient
        saio_mat.ignore_specular = material.ignore_specular

        saio_mat.diffuse = (material.diffuse.x, material.diffuse.y, material.diffuse.z, material.diffuse.w)
        saio_mat.specular = (material.specular.x, material.specular.y, material.specular.z)
        saio_mat.specular_exponent = material.specular_exponent
        saio_mat.ambient = (material.ambient.x, material.ambient.y, material.ambient.z, material.ambient.w)

        saio_mat.use_texture = material.use_texture
        saio_mat.texture_id = material.texture_index
        saio_mat.clamp_u = material.clamp_u
        saio_mat.clamp_v = material.clamp_v
        saio_mat.mirror_u = material.mirror_u
        saio_mat.mirror_v = material.mirror_v
        saio_mat.texturing_mode = 'ENV' if material.environment_mapping else 'UV'
        saio_mat.uv_precision_level = material.texcoord_precision_level
        saio_mat.texture_filtering = enums.TEXTURE_FILTER_MODE[material.texture_filter_mode]
        saio_mat.anisotropic_filtering = material.anisotropic_filtering
        saio_mat.mipmap_distance_multiplier = material.mipmap_distance_multiplier

        ginja_mat: SAIO_Material_Ginja = saio_mat.ginja_properties

        ginja_mat.vertex_color_for_diffuse = material.ginja_use_vertex_color_for_diffuse
        ginja_mat.vertex_color_for_ambient = material.ginja_use_vertex_color_for_ambient
        ginja_mat.texture_slot = material.ginja_texture_slot

        ginja_mat.tevstg_stage = material.ginja_tev_stage_parameter.tev_stage
        ginja_mat.tevstg_tex_coord = material.ginja_tev_stage_parameter.tex_coord
        ginja_mat.tevstg_tex_map = material.ginja_tev_stage_parameter.tex_map
        ginja_mat.tevstg_color_channel = enums.GINJA_COLOR_CHANNEL[material.ginja_tev_stage_parameter.color_channel]

        ginja_mat.texgen_tex_coord = material.ginja_tex_gen_parameter.tex_coord
        ginja_mat.texgen_type = enums.GINJA_TEXGEN_TYPE[material.ginja_tex_gen_parameter.tex_gen_type]
        ginja_mat.texgen_source = enums.GINJA_TEXGEN_SOURCE[material.ginja_tex_gen_parameter.tex_gen_source]
        ginja_mat.texgen_matrix_id = enums.GINJA_MATRIX_ID[material.ginja_tex_gen_parameter.matrix_id]

        return result

    def _convert_materials(self):
        material_indices = []
        for c_material in self._c_materials:
            material_hash = SAIONET.material_get_hash(pointer(c_material))

            material = self._material_lookup.get(material_hash, None)
            if material is None:
                material = self._convert_material(c_material, f"{self._container_name}_{(len(self._material_lookup) + 1)}")
                self._material_lookup[material_hash] = material

            index = self._mesh.materials.find(material.name)
            if index == -1:
                index = len(self._mesh.materials)
                self._mesh.materials.append(material)

        index = 0
        for triangle_set, material_index in zip(self._c_triangle_sets, material_indices):
            for f in range(index, index + len(triangle_set)):
                self._mesh.polygons[f].material_index = material_index
            face_indexindex += len(triangle_set)

    def _convert_normals(self):
        if not self._c_mesh_info.has_normals:
            return

        self._mesh.normals_split_custom_set_from_vertices(
            [i_transform.c_to_bpy_vector(v.normal) for v in self._c_vertices]
        )
        self._mesh.validate()

    def _convert_weights(self):

        if not self._for_armature or self._c_mesh_info.mesh.weight_node_index_map_size == 0 and not self._force_weights:
            return False

        weight_dummy_obj = bpy.data.objects.new("DUMMY", self._mesh)

        if self._node_names is not None:
            get_node_name = lambda node_index: self._node_names[node_index]
        else:
            get_node_name = lambda node_index: f"{node_index:03d}"

        base_group = weight_dummy_obj.vertex_groups.new(name=get_node_name(self._c_mesh_info.attached_node_index))

        if self._c_mesh_info.mesh.weight_node_index_map_size == 0:
            for i, vertex in enumerate(self._c_vertices):
                base_group.add([i], 1, 'REPLACE')

        else:
            groups: list[bpy.types.VertexGroup] = [base_group]
            for i in range(self._c_mesh_info.mesh.weight_node_index_map_size):
                node_index = self._c_mesh_info.attached_node_index + self._c_mesh_info.mesh.weight_node_index_map[i]
                groups.append(weight_dummy_obj.vertex_groups.new(name=get_node_name(node_index)))

            for i, vertex in enumerate(self._c_vertices):
                for j, group in enumerate(groups):
                    weight = vertex.weights[j]
                    if weight > 0:
                        group.add([i], weight, 'REPLACE')

        bpy.data.objects.remove(weight_dummy_obj)

        return True
            
    def _convert_colors(self, color_name: str, get_color: Callable[[CCorner], CVector4]):
        color_attribute = self._mesh.color_attributes.new(color_name, 'FLOAT_COLOR', 'CORNER')

        loop = iter(color_attribute.data)
        for triangle_set in self._c_triangle_sets:
            for corner in triangle_set:
                color = get_color(corner)
                next(loop).color = (color.x, color.y, color.z, color.w)

    def _convert_texcoords(self):
        if not any([m.use_texture for m in self._c_materials]):
            return

        uv_layer = self._mesh.uv_layers.new(name="UVMap", do_init=False)

        index = 0
        for c_triangle_set, c_material in zip(self._c_triangle_sets, self._c_materials):
            if not c_material.use_texture:
                index += len(c_triangle_set)
                continue

            for corner in c_triangle_set:
                uv_layer.uv[index].vector = (corner.tex_coord.x, 1 - corner.tex_coord.y)
                index += 1

    def _convert_mesh(self, mesh_info: CMeshConversionInfo):
        self._c_mesh_info = mesh_info
        self._mesh = bpy.data.meshes.new(mesh_info.mesh.label)

        saio_mesh: SAIO_Mesh = self._mesh.saio_mesh
        saio_mesh.volume_mesh = mesh_info.volume_mesh
        if mesh_info.chunk_vertex_type <= 20:
            saio_mesh.chunk_vertex_type = enums.CHUNK_VERTEX_TYPE[mesh_info.chunk_vertex_type]

        if mesh_info.mesh.vertices_size == 0:
            return self._mesh

        self._prepare_c_data()

        self._convert_geometry()
        self._convert_materials()

        self._convert_normals()
        has_weights = self._convert_weights()

        if mesh_info.has_diffuse_colors:
            self._convert_colors("Diffuse", lambda x: x.diffuse)

        if mesh_info.has_specular_colors:
            self._convert_colors("Specular", lambda x: x.specular)

        self._convert_texcoords()

        return ConvertedMesh(self._mesh, mesh_info, has_weights)


    def convert_meshes(self, container_name: str, node_names: list[str] | None, for_armature: bool, mesh_infos: list[CMeshConversionInfo]) -> list[ConvertedMesh]:
        progress_console.start("Converting Meshes", len(mesh_infos))

        self._container_name = container_name
        self._node_names = node_names
        self._for_armature = for_armature

        result = []

        for i, mesh_info in enumerate(mesh_infos):
            progress_console.update(f"Converting mesh \"{mesh_info.mesh.label}\"", i)
            result.append(self._convert_mesh(mesh_info))

        progress_console.end()

        return result

    def reset(self):
        self._material_lookup.clear()