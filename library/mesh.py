import bpy
from mathutils import Matrix

from . import material


class ModelMesh:

    object: bpy.types.Object
    world_matrix: Matrix
    mesh: bpy.types.Mesh

    root_node_index: int
    armature: bpy.types.Armature

    _viewport_modifier_states: dict[bpy.types.Modifier, bool]
    _armature_modifier: bpy.types.ArmatureModifier
    _edge_split_modifier: bpy.types.EdgeSplitModifier
    _triangulate_modifier: bpy.types.TriangulateModifier

    _evaluted_object: bpy.types.Object
    _evaluted_mesh: bpy.types.Mesh

    def __init__(
            self,
            object: bpy.types.Object,
            root_node_index: int,
            armature: bpy.types.Armature = None):

        self.object = object
        self.world_matrix = object.matrix_world

        self.root_node_index = root_node_index
        self.armature = armature

        self._armature_modifier = None
        self._edge_split_modifier = None
        self._triangulate_modifier = None
        self._viewport_modifier_states = {}

    # Evaluation routine

    def prepare_modifiers(self, apply_modifiers: bool):
        # Whether the model is actually weighted
        weighted = (
            self.armature is not None
            and self.object.parent.data == self.armature
            and self.object.parent_type != 'BONE')

        for modifier in self.object.modifiers:
            self._viewport_modifier_states[modifier] = modifier.show_viewport

            if (weighted
                    and isinstance(modifier, bpy.types.ArmatureModifier)
                    and modifier.object == self.object.parent):
                self._armature_modifier = modifier
                modifier.show_viewport = False

            if not apply_modifiers:
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

    def evaluate(
            self,
            depsgraph,
            apply_modifiers):

        self._evaluted_object = self.object.evaluated_get(depsgraph)

        self._evaluted_mesh = self._evaluted_object.to_mesh(
            preserve_all_data_layers=True,
            depsgraph=depsgraph)

        self._evaluted_mesh.saio_mesh.force_vertex_colors \
            = self.object.data.saio_mesh.force_vertex_colors

    def cleanup_modifiers(self):
        self.object.modifiers.remove(self._triangulate_modifier)
        if self._edge_split_modifier is not None:
            self.object.modifiers.remove(self._edge_split_modifier)

        for modifier in self.object.modifiers:
            modifier.show_viewport = self._viewport_modifier_states[modifier]

    # Conversion Routine

    def _get_normal_matrix(self):
        return self.world_matrix.inverted().transposed().to_3x3()

    def _get_weighted_verts(
            self,
            bone_mapping: dict[str, int],
            node_count: int):

        world_matrix_normal = self._get_normal_matrix()
        vertices = []

        from SATools.SAModel.ModelData.Weighted import WeightedVertex

        groups: list[tuple[bpy.types.VertexGroup, int]] = []
        for group in self._evaluted_object.vertex_groups:
            if group.name not in bone_mapping:
                continue
            groups.append((group, bone_mapping[group.name]))

        for index, vert in enumerate(self._evaluted_mesh.vertices):
            pos = self.world_matrix @ vert.undeformed_co
            nrm = world_matrix_normal @ vert.normal

            # getting weights
            weights = [0 for i in range(node_count)]
            total_weight = 0
            for group, node_index in groups:
                try:
                    weight = group.weight(index)
                    if weight > 0:
                        total_weight += weight
                        weights[node_index] = weight
                except RuntimeError:
                    continue

            # normalizing
            if total_weight == 0:
                weights[self.root_node_index] = 1
            elif total_weight != 1:
                for i in range(node_count):
                    weight = weights[i]
                    if weight > 0:
                        weights[i] = weight / total_weight

            vertices.append(WeightedVertex(
                pos.x, pos.z, -pos.y,
                nrm.x, nrm.z, -nrm.y,
                weights
            ))

        return vertices

    def _get_nonweight_verts(self, node_count: int):
        weights = [0 for i in range(node_count)]
        weights[self.root_node_index] = 1

        world_matrix_normal = self._get_normal_matrix()
        vertices = []

        from SATools.SAModel.ModelData.Weighted import WeightedVertex

        for vert in self._evaluted_mesh.vertices:
            pos = self.world_matrix @ vert.undeformed_co
            nrm = world_matrix_normal @ vert.normal

            vertices.append(WeightedVertex(
                pos.x, pos.z, -pos.y,
                nrm.x, nrm.z, -nrm.y,
                weights
            ))

        return vertices

    def _get_polygon_data(self, context: bpy.types.Context):
        corners: list[list] = []
        materials = []

        for m in self._evaluted_mesh.materials:
            corners.append([])
            materials.append(material.convert_material_to_struct(context, m))

        # if no materials, add default material and corner set
        if len(materials) == 0:
            corners.append([])
            materials.append(material.default_material_struct())

        def get_color(loop, vertex): return (1, 1, 1, 1)
        vertex_colors = self._evaluted_mesh.color_attributes.active
        if vertex_colors is not None:
            if vertex_colors.domain == 'POINT':
                def get_color(loop, vertex):
                    return vertex_colors.data[vertex].color
            else:
                def get_color(loop, vertex):
                    return vertex_colors.data[loop].color

        def get_uv(x): return (0, 0)
        uv_layer = self._evaluted_mesh.uv_layers.active
        if uv_layer is not None:
            def get_uv(x): return uv_layer.data[x].uv

        from SATools.SAModel.ModelData.Buffer import BufferCorner

        for polygon in self._evaluted_mesh.polygons:
            cornerset = corners[polygon.material_index]
            for loop in polygon.loop_indices:
                vert = self._evaluted_mesh.loops[loop].vertex_index
                vcol = get_color(loop, vert)
                uv = get_uv(loop)

                cornerset.append(BufferCorner(
                    vert,
                    vcol[0], vcol[1], vcol[2], vcol[3],
                    uv[0], uv[1]
                ))

        result_materials = []
        result_corners = []

        for i, cornerset in enumerate(corners):
            if len(cornerset) > 0:
                result_materials.append(materials[i])
                result_corners.append(cornerset)

        return result_corners, result_materials

    def convert_to_weighted_buffer(
            self,
            context: bpy.types.Context,
            bone_mapping: dict[str, int],
            node_count: int):

        if bone_mapping is not None and self._armature_modifier is not None:
            vertices = self._get_weighted_verts(bone_mapping, node_count)
        else:
            vertices = self._get_nonweight_verts(node_count)

        corners, materials = self._get_polygon_data(context)

        from SATools.SAModel.Blender import MeshStruct

        return MeshStruct(
            self._evaluted_mesh.name,
            vertices,
            corners,
            materials,
            self._evaluted_mesh.saio_mesh.force_vertex_colors
        )
