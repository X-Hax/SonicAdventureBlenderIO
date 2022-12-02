import bpy
from mathutils import Matrix, Vector

from .o_node import NodeStructure

from ..utility.texture_manager import TexlistManager
from ..utility.color_utils import linear_to_srgb
from ..utility.math_utils import get_normal_matrix


class ModelMesh:

    node_structure: NodeStructure
    object: bpy.types.Object
    world_matrix: Matrix
    attached_node_name: str | None
    '''Name of the node this model is attached to. None for weighted models'''

    _depending_bones: list[str]
    _root_bone_name: str | None
    _root_bone_index: int
    _weight_num: int

    _viewport_modifier_states: dict[bpy.types.Modifier, bool]
    _armature_modifier: bpy.types.ArmatureModifier
    _edge_split_modifier: bpy.types.EdgeSplitModifier
    _triangulate_modifier: bpy.types.TriangulateModifier

    _evaluated_object: bpy.types.Object
    _evaluated_mesh: bpy.types.Mesh

    def __init__(
            self,
            node_structure: NodeStructure,
            object: bpy.types.Object,
            world_matrix: Matrix,
            attached_node_name: str):

        self.node_structure = node_structure
        self.object = object
        self.world_matrix = world_matrix
        self.attached_node_name = attached_node_name

        self._depending_bones = None
        self._root_bone_name = None
        self._root_bone_index = None
        self._weight_num = None

        self._armature_modifier = None
        self._edge_split_modifier = None
        self._triangulate_modifier = None
        self._viewport_modifier_states = {}

    @property
    def _name_mapping(self):
        return self.node_structure.name_mapping

    @property
    def _bones(self):
        return self.node_structure.armature_object.pose.bones

    @property
    def _is_weighted(self):
        return (self.node_structure is not None
                and self.attached_node_name is None)

    # Evaluation routine

    def _prepare_modifiers(self, apply_modifiers: bool):
        # Whether the model is actually weighted
        for modifier in self.object.modifiers:
            self._viewport_modifier_states[modifier] = modifier.show_viewport

            if (self._is_weighted
                    and modifier.type == 'ARMATURE'
                    and modifier.object == self.object.parent):
                self._armature_modifier = modifier
                modifier.show_viewport = False

            elif not apply_modifiers:
                modifier.show_viewport = False

        # add edge split modifier
        if self.object.data.use_auto_smooth:
            self._edge_split_modifier = self.object.modifiers.new(
                "ExportEdgeSplit",
                'EDGE_SPLIT')

            self._edge_split_modifier.split_angle \
                = self.object.data.auto_smooth_angle

            self._edge_split_modifier.use_edge_angle \
                = not self.object.data.has_custom_normals

        # add triangulate modifier
        self._triangulate_modifier = self.object.modifiers.new(
            "ExportTriangulate",
            'TRIANGULATE')
        self._triangulate_modifier.quad_method = 'FIXED'
        self._triangulate_modifier.ngon_method = 'CLIP'
        self._triangulate_modifier.min_vertices = 4
        self._triangulate_modifier.keep_custom_normals = True

    def _collect_depending_bones(self):
        group_indices = {}

        for vertex in self.object.data.vertices:
            for group in vertex.groups:
                if group.weight > 0:
                    group_indices[group.group] = True

        self._depending_bones = []
        for index in group_indices.keys():
            bone_name = self.object.vertex_groups[index].name
            if (bone_name in self._name_mapping
                    and self._bones[bone_name].bone.use_deform):
                self._depending_bones.append(bone_name)

    def _compute_common_root_bone_name(self):
        parent_indices: dict[bpy.types.Bone, int] = {}
        for bone in self._bones:
            parent_indices[bone] = 0

        self._collect_depending_bones()

        for bone_name in self._depending_bones:
            bone = self._bones[bone_name]
            while bone is not None:
                parent_indices[bone] += 1
                bone = bone.parent

        target = len(self._depending_bones)
        for bone, index in reversed(parent_indices.items()):
            if index == target:
                self._root_bone_name = bone.name
                return

        self._root_bone_name = self.node_structure.root_bone_name

    def _eval_weight_structure(self):
        self._collect_depending_bones()
        self._compute_common_root_bone_name()

        self._root_bone_index = self._name_mapping[self._root_bone_name]

        max_node_index = max(
            [self._name_mapping[x] for x in self._depending_bones])

        self._weight_num = max_node_index - self._root_bone_index + 1

    def _evaluate(self, depsgraph: bpy.types.Depsgraph):
        self._evaluated_object = self.object.evaluated_get(depsgraph)

        if self._evaluated_object.data.shape_keys is not None:
            for shape_key in self._evaluated_object.data.shape_keys.key_blocks:
                shape_key.value = 0

        self._evaluated_mesh = self._evaluated_object.to_mesh(
            preserve_all_data_layers=True,
            depsgraph=depsgraph)

        if self._is_weighted:
            self._eval_weight_structure()

    def _cleanup_modifiers(self):
        self.object.modifiers.remove(self._triangulate_modifier)
        if self._edge_split_modifier is not None:
            self.object.modifiers.remove(self._edge_split_modifier)

        for modifier in self.object.modifiers:
            modifier.show_viewport = self._viewport_modifier_states[modifier]

    def get_shape_model(
            self,
            keyframe_name: str,
            depsgraph: bpy.types.Depsgraph):

        shape_keys = self._evaluated_object.data.shape_keys.key_blocks
        if keyframe_name not in shape_keys:
            return None

        for shape_key in shape_keys:
            if shape_key.name == keyframe_name:
                shape_key.value = 1
            else:
                shape_key.value = 0

        return self._evaluated_object.to_mesh(
            preserve_all_data_layers=True,
            depsgraph=depsgraph)

    # Conversion routine

    @staticmethod
    def get_normals(mesh: bpy.types.Mesh):
        normals = [vert.normal for vert in mesh.vertices]
        if not mesh.use_auto_smooth:
            return normals

        split_normals = [Vector() for _ in normals]
        split_normal_count = [0] * len(normals)

        mesh.calc_normals_split()
        for loop, normal in zip(mesh.loops, mesh.corner_normals):
            split_normals[loop.vertex_index] += normal.vector
            split_normal_count[loop.vertex_index] += 1

        for index, count in enumerate(split_normal_count):
            if count > 0:
                normals[index] = split_normals[index] / count

        return normals

    def _get_normals(self):
        return ModelMesh.get_normals(self._evaluated_mesh)

    def get_matrices(self) -> tuple[Matrix, Matrix]:
        if self._is_weighted:
            target = self.node_structure.node_matrices[self._root_bone_name]
        else:
            target = self.node_structure.node_matrices[self.attached_node_name]

        vertex_matrix: Matrix = target.inverted() @ self.world_matrix
        normal_matrix = get_normal_matrix(vertex_matrix)

        return vertex_matrix, normal_matrix

    def _get_weighted_verts(self):

        vertex_matrix, normal_matrix = self.get_matrices()
        normals = self._get_normals()

        from SA3D.Modeling.ModelData.Weighted import WeightedBufferVertex
        from System.Numerics import Vector3
        buffer_vertices = []

        groups: list[tuple[bpy.types.VertexGroup, int]] = []
        for group in self._evaluated_object.vertex_groups:
            if group.name not in self._depending_bones:
                continue

            groups.append((
                group,
                self._name_mapping[group.name]
                - self._root_bone_index))

        for index, vert in enumerate(self._evaluated_mesh.vertices):
            pos = vertex_matrix @ vert.undeformed_co
            nrm = normal_matrix @ normals[index]

            wbv = WeightedBufferVertex(
                Vector3(pos.x, pos.z, -pos.y),
                Vector3(nrm.x, nrm.z, -nrm.y),
                self._weight_num)

            # getting weights
            total_weight = 0
            for group, node_index in groups:
                try:
                    weight = group.weight(index)
                except RuntimeError:
                    continue
                if weight > 0:
                    total_weight += weight
                    wbv.Weights[node_index] = weight

            # normalizing
            if total_weight == 0:
                wbv.Weights[0] = 1
            elif total_weight != 1:
                for i, weight in enumerate(wbv.Weights):
                    if weight > 0:
                        wbv.Weights[i] /= total_weight

            buffer_vertices.append(wbv)

        return buffer_vertices

    def _get_nonweight_verts(self):
        vertices = []
        normals = self._get_normals()

        from SA3D.Modeling.ModelData.Weighted import WeightedBufferVertex
        from System.Numerics import Vector3

        def add_vertex(pos, nrm):
            vertices.append(WeightedBufferVertex(
                Vector3(pos.x, pos.z, -pos.y),
                Vector3(nrm.x, nrm.z, -nrm.y)
            ))

        if self.node_structure.armature_object is None:
            # No armature = no space conversion needed, since the attaches are
            # directly located on the objects

            for vertex, normal in zip(self._evaluated_mesh.vertices, normals):
                pos = vertex.undeformed_co
                add_vertex(pos, normal)

        else:
            # Armature = space conversion needed, as meshes' transformation
            # may not match that of the bones
            vertex_matrix, normal_matrix = self.get_matrices()

            for vertex, normal in zip(self._evaluated_mesh.vertices, normals):
                pos = vertex_matrix @ vertex.undeformed_co
                nrm = normal_matrix @ normal
                add_vertex(pos, nrm)

        return vertices

    def _get_raw_verts(self):
        vertices = []
        normals = self._get_normals()

        from SA3D.Modeling.ModelData.Weighted import WeightedBufferVertex
        from System.Numerics import Vector3

        for vertex, nrm in zip(self._evaluated_mesh.vertices, normals):
            pos = vertex.undeformed_co
            vertices.append(WeightedBufferVertex(
                Vector3(pos.x, pos.z, -pos.y),
                Vector3(nrm.x, nrm.z, -nrm.y)
            ))

        return vertices

    def _get_polygon_data(self, texlist_manager: TexlistManager):
        from . import o_material

        corners: list[list] = []
        materials = []

        for m in self._evaluated_mesh.materials:
            corners.append([])
            materials.append(
                o_material.convert_material_to_struct(m, texlist_manager))

        # if no materials, add default material and corner set
        if len(materials) == 0:
            corners.append([])
            materials.append(o_material.default_material_struct())

        # Color obtainer

        def get_color(loop, vertex): return (1, 1, 1, 1)
        vertex_colors = self._evaluated_mesh.color_attributes.active_color
        if vertex_colors is not None:
            if vertex_colors.domain == 'POINT':
                def get_color(loop, vertex):
                    return linear_to_srgb(vertex_colors.data[vertex].color)
            else:
                def get_color(loop, vertex):
                    return linear_to_srgb(vertex_colors.data[loop].color)

        # UV Obtainer

        def get_uv(x): return (0, 0)
        uv_layer = self._evaluated_mesh.uv_layers.active
        if uv_layer is not None:
            def get_uv(x): return uv_layer.data[x].uv

        # Collecting the data

        from SA3D.Modeling.ModelData.Buffer import BufferCorner

        for polygon in self._evaluated_mesh.polygons:
            cornerset = corners[polygon.material_index]
            for loop in polygon.loop_indices:
                vert = self._evaluated_mesh.loops[loop].vertex_index
                vcol = get_color(loop, vert)
                uv = get_uv(loop)

                cornerset.append(BufferCorner(
                    vert,
                    vcol[0], vcol[1], vcol[2], vcol[3],
                    uv[0], 1 - uv[1]
                ))

        result_materials = []
        result_corners = []

        for i, cornerset in enumerate(corners):
            if len(cornerset) > 0:
                result_materials.append(materials[i])
                result_corners.append(cornerset)

        if len(result_corners) == 0:
            raise Exception("Empty mesh!")

        return result_corners, result_materials

    def convert_to_weighted_buffer(self, texlist_manager):

        if self.node_structure is None:
            root_index = 0
            vertices = self._get_raw_verts()
        elif self._is_weighted:
            root_index = self._root_bone_index
            vertices = self._get_weighted_verts()
        else:
            root_index = self._name_mapping[self.attached_node_name]
            vertices = self._get_nonweight_verts()

        corners, materials = self._get_polygon_data(texlist_manager)

        from SA3D.Modeling.Blender import MeshStruct

        return MeshStruct(
            self._evaluated_mesh.name,
            vertices,
            corners,
            materials,
            root_index,
            len(self._evaluated_mesh.color_attributes) > 0,
            self.object.data.saio_mesh.force_vertex_colors
        )

    @staticmethod
    def evaluate_models(
            context: bpy.types.Context,
            meshes: list['ModelMesh'],
            apply_modifiers: bool,
            convert: bool = True):

        for mesh in meshes:
            mesh._prepare_modifiers(apply_modifiers)

        texlist_manager = TexlistManager()
        texlist_manager.evaluate_texlists(context.scene)

        depsgraph = context.evaluated_depsgraph_get()

        mesh_structs = []
        for mesh in meshes:
            mesh._evaluate(depsgraph)

            if convert:
                weighted_buffer = mesh.convert_to_weighted_buffer(
                    texlist_manager)
                mesh_structs.append(weighted_buffer)

        for mesh in meshes:
            mesh._cleanup_modifiers()

        return mesh_structs
