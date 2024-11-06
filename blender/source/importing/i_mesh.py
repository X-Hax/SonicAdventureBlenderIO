import bpy
from mathutils import Vector

from . import i_enum

from ..utility import material_setup
from ..register.property_groups.material_properties import SAIO_Material
from ..utility.color_utils import srgb_to_linear


class MeshData:

    mesh: bpy.types.Mesh

    weights: list[list[tuple[int, float]]]
    '''[group index][x] = (vertex index, weight)'''

    node_indices: list[int]

    def __init__(self, weight_group_num: int, node_indices: list[int]):
        self.mesh = None
        self.weights = []
        for _ in range(weight_group_num):
            self.weights.append([])
        self.node_indices = node_indices

    @property
    def is_weighted(self):
        return len(self.weights) > 0


class MeshProcessor:

    _auto_normals: bool

    material_lut: dict[any, bpy.types.Material]

    weighted_buffer: any
    name: str
    mat_name: str

    vertices: list[Vector]
    normals: list[Vector]
    polygons: list[tuple[int, int, int]]
    materials: list[bpy.types.Material]
    poly_material_lengths: list[int]
    colors: list[tuple[float, float, float, float]]
    uvs: list[tuple[float, float]]
    import_normals: bool

    output: MeshData

    def __init__(
            self,
            auto_normals: bool):

        self._auto_normals = auto_normals

        self.material_lut = {}

        self.vertices = []
        self.normals = []
        self.polygons = []
        self.materials = []
        self.poly_material_lengths = []
        self.colors = []
        self.uvs = []

        self.name = None
        self.output = None

    #########################################################

    def _to_color(self, color):
        return (color.RedF, color.GreenF, color.BlueF, color.AlphaF)

    def _net_to_bpy_material(self, material, name: str):
        bpy_material = bpy.data.materials.new(name)
        props: SAIO_Material = bpy_material.saio_material

        props.diffuse = self._to_color(material.Diffuse)
        props.specular = self._to_color(material.Specular)
        props.specular_exponent = int(material.SpecularExponent)
        props.ambient = self._to_color(material.Ambient)

        props.texture_id = material.TextureIndex
        props.texture_filtering = i_enum.from_filter_mode(material.TextureFiltering)
        props.mipmap_distance_multiplier = material.MipmapDistanceMultiplier
        props.source_alpha = i_enum.from_blend_mode(material.SourceBlendMode)
        props.destination_alpha = i_enum.from_blend_mode(material.DestinationBlendmode)

        props.anisotropic_filtering = material.AnisotropicFiltering
        props.use_alpha = material.UseAlpha
        props.double_sided = not material.BackfaceCulling
        props.no_alpha_test = material.NoAlphaTest
        props.flat_shading = material.Flat
        props.ignore_ambient = material.NoAmbient
        props.ignore_diffuse = material.NoLighting
        props.ignore_specular = material.NoSpecular
        props.use_texture = material.UseTexture
        props.use_environment = material.NormalMapping
        props.clamp_u = material.ClampU
        props.mirror_u = material.MirrorU
        props.clamp_v = material.ClampV
        props.mirror_v = material.MirrorV

        props.shadow_stencil = material.GCShadowStencil
        props.texgen_coord_id = i_enum.from_tex_coord_id(material.GCTexCoordID)
        props.texgen_type = i_enum.from_tex_gen_type(material.GCTexCoordType)
        props.texgen_source = i_enum.from_tex_gen_source(material.GCTexCoordSource)
        props.texgen_matrix_id = i_enum.from_tex_gen_matrix(material.GCMatrixID)

        return bpy_material

    #########################################################

    def _setup_buffers(self):
        self.vertices.clear()
        self.normals.clear()
        self.polygons.clear()
        self.materials.clear()
        self.poly_material_lengths.clear()
        self.colors.clear()
        self.uvs.clear()

    def _setup_output(self):
        weight_group_num = 0

        if self.weighted_buffer.IsWeighted:
            for node_index in self.weighted_buffer.DependingNodeIndices:
                if node_index > weight_group_num:
                    weight_group_num = node_index
            weight_group_num += 1

        self.output = MeshData(
            weight_group_num,
            list(self.weighted_buffer.RootIndices))

    #########################################################

    def _process_vertices(self):
        for index, vert in enumerate(self.weighted_buffer.Vertices):
            pos = vert.Position
            self.vertices.append(Vector((pos.X, -pos.Z, pos.Y)))

            nrm = vert.Normal
            self.normals.append(Vector((nrm.X, -nrm.Z, nrm.Y)))

            if vert.Weights is not None:
                for weight_index, weight in enumerate(vert.Weights):
                    if weight > 0:
                        self.output.weights[weight_index].append(
                            (index, weight))

    def _process_corner(self, corner: any):
        uv = corner.Texcoord
        self.uvs.append((uv.X, 1 - uv.Y))

        color = corner.Color
        color = (color.RedF, color.GreenF, color.BlueF, color.AlphaF)
        color = srgb_to_linear(color)
        self.colors.append(color)

    def _process_polygons(self):
        for cornerset in self.weighted_buffer.TriangleSets:
            for index in range(0, len(cornerset), 3):
                c1 = cornerset[index]
                c2 = cornerset[index+1]
                c3 = cornerset[index+2]

                self.polygons.append((
                    c1.VertexIndex,
                    c2.VertexIndex,
                    c3.VertexIndex))

                self._process_corner(c1)
                self._process_corner(c2)
                self._process_corner(c3)

            self.poly_material_lengths.append(len(cornerset) / 3)

    def _process_materials(self):

        for material in self.weighted_buffer.Materials:
            hashcode = material.GetHashCode()
            if hashcode in self.material_lut:
                bpy_material = self.material_lut[hashcode]
            else:
                bpy_material = self._net_to_bpy_material(
                    material, f"{self.mat_name}_{len(self.material_lut)}")
                self.material_lut[hashcode] = bpy_material

            self.materials.append(bpy_material)

    #########################################################

    def _setup_mesh_polygons(self):
        if len(self.poly_material_lengths) > 1:

            poly_mat_index = 0
            next_material_offset = self.poly_material_lengths[poly_mat_index]

            for i, polygon in enumerate(self.output.mesh.polygons):

                if i >= next_material_offset:
                    poly_mat_index += 1
                    next_material_offset += self.poly_material_lengths[poly_mat_index]

                polygon.use_smooth = self.import_normals
                polygon.material_index = poly_mat_index

        else:
            for polygon in self.output.mesh.polygons:
                polygon.use_smooth = self.import_normals

    def _setup_mesh_normals(self):
        if self.import_normals:
            self.output.mesh.normals_split_custom_set_from_vertices(self.normals)

    def _setup_mesh_colors(self):
        if self.weighted_buffer.HasColors:
            color_attributes = self.output.mesh.color_attributes.new(
                "Color", 'FLOAT_COLOR', 'CORNER')

            for i, color in enumerate(self.colors):
                color_attributes.data[i].color = color

    def _setup_mesh_uvs(self):
        uv_layer = self.output.mesh.uv_layers.new(name="UV")
        for i, uv in enumerate(self.uvs):
            uv_layer.data[i].uv = uv

    def _create_mesh(self):
        self.output.mesh = bpy.data.meshes.new(self.name)
        self.output.mesh.from_pydata(self.vertices, [], self.polygons)
        self.output.mesh.saio_mesh.texcoord_precision_level = self.weighted_buffer.TexcoordPrecisionLevel

        for mat in self.materials:
            self.output.mesh.materials.append(mat)

        self.import_normals = self.weighted_buffer.HasNormals or not self._auto_normals

        self._setup_mesh_polygons()
        self._setup_mesh_normals()
        self._setup_mesh_colors()
        self._setup_mesh_uvs()

    #########################################################

    def process(self, weighted_buffer, name: str, mat_name: str | None = None):

        if weighted_buffer.Label is not None:
            name = weighted_buffer.Label

        self.name = name
        self.mat_name = name if mat_name is None else mat_name
        self.weighted_buffer = weighted_buffer

        self._setup_buffers()
        self._setup_output()

        self._process_vertices()
        self._process_polygons()
        self._process_materials()

        self._create_mesh()

    def process_multiple(
            self,
            weighted_buffers,
            name: str,
            mat_name: str | None = None):
        result: list[MeshData] = []

        if mat_name is None:
            mat_name = name

        for weighted_buffer in weighted_buffers:
            if weighted_buffers.Length > 1:
                mesh_name = f"{name}_{len(result)}"
            else:
                mesh_name = name

            self.process(
                weighted_buffer,
                mesh_name,
                mat_name
            )
            result.append(self.output)

        return result

    def setup_materials(self, context: bpy.types.Context):
        material_setup.setup_and_update_materials(
            context, self.material_lut.values())

    @staticmethod
    def process_meshes(
            context: bpy.types.Context,
            weighted_buffers,
            name: str,
            mat_name: str | None = None,
            auto_normals: bool = True):

        processor = MeshProcessor(auto_normals)
        result = processor.process_multiple(weighted_buffers, name, mat_name)
        processor.setup_materials(context)
        return result
