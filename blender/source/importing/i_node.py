import bpy
from mathutils import Matrix, Vector, Quaternion

from . import i_enum, i_matrix, i_mesh
from ..exceptions import SAIOException

class NodeProcessor:

    _context: bpy.types.Context
    _collection: bpy.types.Collection
    _merge_meshes: bool
    _mesh_processor: i_mesh.MeshProcessor

    ensure_order: bool
    object_map: dict[any, bpy.types.Object]
    meshes: list[i_mesh.MeshData]
    node_name_lut: dict[str, str]

    _armature: bpy.types.Armature
    _armature_obj: bpy.types.Object

    _bone_map: dict
    _node_map: dict
    _pose_matrices: list

    def __init__(
            self,
            context: bpy.types.Context,
            collection: bpy.types.Collection,
            ensure_order: bool,
            merge_meshes: bool,
            node_name_lut: dict[str, str] | None = None):

        self._context = context
        self._collection = collection
        self.ensure_order = ensure_order
        self._merge_meshes = merge_meshes
        self._mesh_processor = i_mesh.MeshProcessor()

        self.object_map = {}
        self.meshes = []

        if node_name_lut is None:
            self.node_name_lut = {}
        else:
            self.node_name_lut = node_name_lut

    def _eval_name(self, index: int, name: str):
        if self.ensure_order:
            return f"{index:03}_{name}"
        else:
            return name

    def _create_mesh_object(self, mesh: bpy.types.Mesh, index: int):
        name = mesh.name
        if index is not None:
            name = f"{mesh.name}_{index}"

        mesh_obj = bpy.data.objects.new(name, mesh)

        self._collection.objects.link(mesh_obj)
        mesh_obj.parent = self._armature_obj

        return mesh_obj

    #########################################################

    def _setup_armature(self, name: str):
        self._armature = bpy.data.armatures.new(name)
        self._armature_obj = bpy.data.objects.new(
            self._armature.name,
            self._armature)

        self._collection.objects.link(self._armature_obj)

        self._context.view_layer.objects.active = self._armature_obj

        self._bone_map = {}
        self._node_map = {}
        self._pose_matrices = []

    def _set_bone_transforms(
            self,
            bone: bpy.types.Bone,
            matrices: list[Matrix]):

        bone.head = (0, 0, 0)
        bone.tail = (1, 0, 0)

        # getting the local matrix
        local_space = matrices[self._bone_map[bone.name]]

        if bone.parent is not None:
            parent_index = self._bone_map[bone.parent.name]
            local_space = matrices[parent_index].inverted() @ local_space
            parent_matrix = bone.parent.matrix
        else:
            parent_matrix = Matrix.Identity(4)

        # getting the scale matrix
        _, _, scale = local_space.decompose()
        local_scale = Matrix.LocRotScale(
            Vector(), Quaternion(), scale)
        self._pose_matrices.append(local_scale)

        # finding the unscaled bone matrix
        bone_matrix = parent_matrix @ local_space
        pos, rot, _ = bone_matrix.decompose()

        bone.matrix = Matrix.LocRotScale(pos, rot, None)

    def _create_bones(self, nodes, matrices: list[Matrix]):
        for index, node in enumerate(nodes):
            bone = self._armature.edit_bones.new(
                self._eval_name(index, node.Label))

            self._bone_map[bone.name] = index
            self._bone_map[index] = bone.name
            self._node_map[node] = bone
            self.node_name_lut[node.Label] = \
                f"{self._armature_obj.name}\n{bone.name}"

            if node.Parent in self._node_map:
                bone.parent = self._node_map[node.Parent]

            i_enum.from_node_attributes(bone.saio_node, node.Attributes)

            self._set_bone_transforms(bone, matrices)

    def _correct_bone_lengths(self):
        for bone in self._armature.edit_bones:
            if len(bone.children) == 0:
                continue

            distance = float("inf")
            for child in bone.children:
                new_distance = (bone.head - child.head).magnitude
                if new_distance < distance:
                    distance = new_distance

            if distance < 0.5:
                distance = 0.5
            bone.length = distance

    def _pre_bone_scale_correct(self):
        # correcting pose bone scales. we invert them first, so that we can
        # apply the armature modifier to get the "correct" mesh
        for pose_bone in self._armature_obj.pose.bones:
            pose_bone.matrix_basis = self._pose_matrices[
                self._bone_map[pose_bone.name]]
            pose_bone.matrix_basis.invert()

    def _post_bone_scale_correct(self):
        # correcting them after applying armature modifier
        for pose_bone in self._armature_obj.pose.bones:
            pose_bone.matrix_basis.invert()

    #########################################################

    def _setup_mesh_bone_parent(
            self,
            mesh_obj: bpy.types.Object,
            node_index: int):

        bone_name = self._bone_map[node_index]
        mesh_obj.parent_type = 'BONE'
        mesh_obj.parent_bone = bone_name
        self._context.view_layer.update()

    def _setup_mesh_bone_transforms(self, mesh_obj: bpy.types.Object):
        bone = self._armature_obj.pose.bones[mesh_obj.parent_bone]
        bone_matrix = self._armature_obj.matrix_world @ bone.matrix

        mesh_obj.matrix_parent_inverse = (
            mesh_obj.matrix_world.inverted() @ bone_matrix
        )

    def _setup_unweighted_mesh(self, meshdata: i_mesh.MeshData, index: int):
        mesh_obj = self._create_mesh_object(meshdata.mesh, index)

        self._setup_mesh_bone_parent(
            mesh_obj,
            meshdata.node_indices[
                0 if index is None else index])
        self._setup_mesh_bone_transforms(mesh_obj)

        # prepare for merging
        if self._merge_meshes:
            group = mesh_obj.vertex_groups.new(name=mesh_obj.parent_bone)
            group.add(range(len(meshdata.mesh.vertices)), 1, 'REPLACE')

    #########################################################

    def _align_with_bone_transforms(
            self,
            mesh_obj: bpy.types.Object,
            node_index: int):

        bone_name = self._bone_map[node_index]
        bone = self._armature_obj.pose.bones[bone_name]
        bone_matrix = self._armature_obj.matrix_world @ bone.matrix
        mesh_obj.matrix_world = bone_matrix

    def _setup_mesh_weights(
            self,
            mesh_obj: bpy.types.Object,
            meshdata: i_mesh.MeshData,
            node_index: int):

        for bone_index, bone_weights in enumerate(meshdata.weights):
            if len(bone_weights) == 0:
                continue
            bone_name = self._bone_map[bone_index + node_index]
            weight_group = mesh_obj.vertex_groups.new(name=bone_name)
            for vertex_index, weight in bone_weights:
                weight_group.add([vertex_index], weight, 'REPLACE')

    def _setup_mesh_modifiers(self, mesh_obj: bpy.types.Object):
        # The mesh got exported with "applied scales", so to compensate
        # that, we inverted the pose bone scales before. Now we apply the
        # armature deform to get the "correct" mesh, add a real modifier,
        # and later invert the pose bone scales again. As ridiculous as it
        # sounds, this works!

        armature_modifier: bpy.types.ArmatureModifier \
            = mesh_obj.modifiers.new("Armature", 'ARMATURE')
        armature_modifier.object = self._armature_obj

        bpy.context.view_layer.objects.active = mesh_obj
        bpy.ops.object.modifier_apply(
            modifier=armature_modifier.name)

        armature_modifier: bpy.types.ArmatureModifier \
            = mesh_obj.modifiers.new("Armature", 'ARMATURE')
        armature_modifier.object = self._armature_obj

    def _setup_weighted_mesh(
            self,
            meshdata: i_mesh.MeshData,
            index: int | None):

        mesh = meshdata.mesh.copy()

        if index is not None:
            mesh.name = f"{meshdata.mesh.name}_{index}"
        else:
            mesh.name = meshdata.mesh.name

        mesh_obj = self._create_mesh_object(mesh, index)

        node_index = meshdata.node_indices[0 if index is None else index]

        self._align_with_bone_transforms(mesh_obj, node_index)
        self._setup_mesh_weights(mesh_obj, meshdata, node_index)
        self._setup_mesh_modifiers(mesh_obj)

    def _merge_armature_meshes(self):
        pose_info = {}
        for bone in self._armature_obj.pose.bones:
            pose_info[bone.name] = bone.matrix_basis.copy()
            bone.matrix_basis = Matrix.Identity(4)

        bpy.ops.object.select_all(action='DESELECT')
        for mesh_obj in self._armature_obj.children:
            mesh_obj.select_set(True)

        target_mesh = bpy.data.meshes.new("Armature_Mesh")
        target_mesh_obj = bpy.data.objects.new(
            "Armature_Mesh", target_mesh)
        self._collection.objects.link(target_mesh_obj)
        target_mesh_obj.parent = self._armature_obj

        target_mesh_obj.select_set(True)
        self._context.view_layer.objects.active = target_mesh_obj

        bpy.ops.object.join()
        bpy.ops.object.select_all(action='DESELECT')

        armature_modifier: bpy.types.ArmatureModifier \
            = target_mesh_obj.modifiers.new("Armature", 'ARMATURE')
        armature_modifier.object = self._armature_obj

        for bone_name, matrix in pose_info.items():
            bone = self._armature_obj.pose.bones[bone_name]
            bone.matrix_basis = matrix

    #########################################################

    def process_as_armature(self, nodes, name: str):

        prev_ensure_order = self.ensure_order
        if len(nodes) == 1:
            self.ensure_order = False

        net_matrices = [node_matrix.Item2 for node_matrix in nodes[0].GetWorldMatrixTree()]
        matrices = i_matrix.net_to_bpy_matrices(net_matrices)

        self._setup_armature(name)

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        self._create_bones(nodes, matrices)
        self._correct_bone_lengths()

        bpy.ops.object.mode_set(mode='OBJECT')

        self._pre_bone_scale_correct()
        for mesh in self.meshes:
            for i in range(len(mesh.node_indices)):
                if len(mesh.node_indices) == 1:
                    i = None
                if mesh.is_weighted:
                    self._setup_weighted_mesh(mesh, i)
                else:
                    self._setup_unweighted_mesh(mesh, i)

        self._post_bone_scale_correct()

        if self._merge_meshes:
            self._merge_armature_meshes()

        self.ensure_order = prev_ensure_order

    def process_as_objects(self, nodes):

        prev_ensure_order = self.ensure_order
        if len(nodes) == 1:
            self.ensure_order = False

        net_matrices = [node_matrix.Item2 for node_matrix in nodes[0].GetWorldMatrixTree()]
        matrices = i_matrix.net_to_bpy_matrices(net_matrices)

        mesh_dict: dict[int, i_mesh.MeshData] = {}
        for mesh in self.meshes:
            for node_index in mesh.node_indices:
                if node_index in mesh_dict:
                    raise SAIOException("Duplicate node index in meshes!")
                mesh_dict[node_index] = mesh

        for index, node in enumerate(nodes):
            data = None
            if index in mesh_dict:
                data = mesh_dict[index].mesh

            name = node.Label
            if len(nodes) > 1:
                name = self._eval_name(index, node.Label)

            obj = bpy.data.objects.new(name, data)
            self.node_name_lut[node.Label] = obj.name

            obj.empty_display_type = 'ARROWS'
            self.object_map[node] = obj
            self._collection.objects.link(obj)

            i_enum.from_node_attributes(
                obj.saio_node,
                node.Attributes)

            if node.Parent in self.object_map:
                parent_object = self.object_map[node.Parent]
                obj.parent = parent_object

            obj.matrix_world = matrices[index]

        self.ensure_order = prev_ensure_order

    def process(
            self,
            import_data,
            name: str,
            mat_name: str | None = None,
            force_armature: bool = False):

        self.meshes = self._mesh_processor.process_multiple(
            import_data.Attaches,
            name,
            mat_name
        )

        nodes = import_data.Root.GetTreeNodes()
        if force_armature or import_data.Weighted:
            self.process_as_armature(nodes, name)
        else:
            self.process_as_objects(nodes)

    def setup_materials(self):
        self._mesh_processor.setup_materials(self._context)

    @staticmethod
    def process_model(
            context: bpy.types.Context,
            import_data,
            collection: bpy.types.Collection,
            name: str,
            mat_name: str | None = None,
            node_name_lut: dict[str, str] | None = None,
            force_armature: bool = False,
            merge_meshes: bool = False,
            ensure_order: bool = True):

        node_processor = NodeProcessor(
            context,
            collection,
            ensure_order,
            merge_meshes,
            node_name_lut
        )

        node_processor.process(import_data, name, mat_name, force_armature)
        node_processor.setup_materials()
