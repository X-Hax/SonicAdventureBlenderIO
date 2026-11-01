from enum import Enum
import bpy
from mathutils import Matrix, Vector, Quaternion

from . import i_mesh, i_transform

from ..external import CModel, CNode, CMeshConversionInfo
from ..register.property_groups.node_properties import SAIO_Node
from ..exceptions import SAIODevException


class ModelConverter:

    # Parameters
    _mesh_converter: i_mesh.MeshConverter
    _context: bpy.types.Context

    _ensure_order: bool
    _force_armature: bool
    _bone_orientation: str
    _bone_length_mode: str
    _min_bone_length: float
    _max_leaf_bone_length: float
    _merge_meshes: bool

    # Session context
    _collection: bpy.types.Collection
    _model: CModel

    _c_nodes: list[CNode]
    _node_names: list[str]
    _meshes: list[i_mesh.ConvertedMesh]

    _armature: bpy.types.Armature
    _armature_obj: bpy.types.Object
    _local_matrices: list[Matrix]

    def __init__(
            self,
            mesh_converter: i_mesh.MeshConverter,
            context: bpy.types.Context,
            ensure_order: bool,
            force_armature: bool,
            bone_orientation: str,
            bone_length_mode: str,
            min_bone_length: float,
            max_leaf_bone_length: float,
            merge_meshes: bool):

        self._mesh_converter = mesh_converter
        self._context = context

        self._ensure_order = ensure_order
        self._force_armature = force_armature
        self._bone_orientation = bone_orientation
        self._bone_length_mode = bone_length_mode
        self._min_bone_length = min_bone_length
        self._max_leaf_bone_length = max_leaf_bone_length
        self._merge_meshes = merge_meshes


    @staticmethod
    def _setup_node_attributes(saio_node: SAIO_Node, c_node: CNode):
        saio_node.no_animate = c_node.no_animate
        saio_node.no_morph = c_node.no_morph
        saio_node.clip = c_node.clip
        saio_node.cache_rotation = c_node.cache_rotation
        saio_node.apply_cached_rotation = c_node.apply_cached_rotation

    def _convert_nodes_to_objects(self):

        matrices = [i_transform.c_to_bpy_matrix(node.transform) for node in self._c_nodes]

        mesh_dict: dict[int, bpy.types.Mesh] = {}
        for mesh in self._meshes:
            mesh_dict[mesh.mesh_info.attached_node_index] = mesh.mesh

        objects = []

        for index, node in enumerate(self._c_nodes):
            data = mesh_dict.get(index, None)
            obj = bpy.data.objects.new(self._node_names[index], data)

            obj.empty_display_type = 'ARROWS'
            self._setup_node_attributes(obj.saio_node, node)

            self._collection.objects.link(obj)

            if node.parent_index >= 0:
                obj.parent = objects[node.parent_index]

            obj.matrix_local = matrices[index]

            objects.append(obj)

        return objects[0]

    #########################################################

    def _setup_armature(self):
        self._armature = bpy.data.armatures.new(self._model.name)
        self._armature_obj = bpy.data.objects.new(
            self._armature.name,
            self._armature)

        self._collection.objects.link(self._armature_obj)
        self._context.view_layer.objects.active = self._armature_obj

        if self._bone_orientation == 'XZ':
            convert_matrix = i_transform.c_to_bpy_bone_xz_matrix
        else:
            convert_matrix = i_transform.c_to_bpy_matrix

        self._local_matrices = [convert_matrix(node.transform) for node in self._c_nodes]


    def _create_bones(self):
        for index, node in enumerate(self._c_nodes):
            bone = self._armature.edit_bones.new(self._node_names[index])

            if node.parent_index >= 0:
                bone.parent = self._armature.edit_bones[node.parent_index]
                parent_world_matrix = bone.parent.matrix
            else:
                parent_world_matrix = Matrix.Identity(4)

            self._setup_node_attributes(bone.saio_node, node)

            bone.head = (0, 0, 0)
            bone.tail = (0, 1, 0)
            bone.matrix = (parent_world_matrix @ self._local_matrices[index].normalized())

    @staticmethod
    def _get_bone_length_closest(bone: bpy.types.EditBone):
        distance = float("inf")

        for child in bone.children:
            new_distance = (bone.head - child.head).magnitude
            if new_distance < distance:
                distance = new_distance

        return distance

    @staticmethod
    def _get_bone_length_furthest(bone: bpy.types.EditBone):
        distance = float(0)

        for child in bone.children:
            new_distance = (bone.head - child.head).magnitude
            if new_distance > distance:
                distance = new_distance

        return distance

    @staticmethod
    def _get_bone_length_most_children(bone: bpy.types.EditBone):
        parent_bone = bone.children[0]

        for child in bone.children[1:]:
            if len(child.children) > len(parent_bone.children):
                parent_bone = child

        return (bone.head - parent_bone.head).magnitude

    @staticmethod
    def _get_bone_length_first(bone: bpy.types.EditBone):
        return (bone.head - bone.children[0].head).magnitude

    def _correct_bone_lengths(self):
        for bone in self._armature.edit_bones:
            if len(bone.children) > 0:

                if self._bone_length_mode == 'CLOSEST':
                    distance = self._get_bone_length_closest(bone)
                elif self._bone_length_mode == 'FURTHEST':
                    distance = self._get_bone_length_furthest(bone)
                elif self._bone_length_mode == 'MOSTCHILDREN':
                    distance = self._get_bone_length_most_children(bone)
                elif self._bone_length_mode == 'FIRST':
                    distance = self._get_bone_length_first(bone)
                else:
                    raise SAIODevException("Invalid bone length mode")

                distance = max(distance, self._min_bone_length)

            elif bone.parent is not None:
                distance = min(self._max_leaf_bone_length, bone.parent.length)

            else:
                continue

            bone.length = distance

    def _pre_bone_scale_correct(self):
        # correcting pose bone scales. we invert them first, so that we can
        # apply the armature modifier to get the "correct" mesh
        for pose_bone, local_matrix in zip(self._armature_obj.pose.bones, self._local_matrices):
            _, _, scale = local_matrix.decompose()
            pose_bone.matrix_basis = Matrix.LocRotScale(None, None, scale)
            pose_bone.matrix_basis.invert()

    def _post_bone_scale_correct(self):
        # correcting them after applying armature modifier
        for pose_bone in self._armature_obj.pose.bones:
            pose_bone.matrix_basis.invert()

    #########################################################

    def _create_mesh_object(self, mesh: bpy.types.Mesh):
        mesh_obj = bpy.data.objects.new(mesh.name, mesh)

        self._collection.objects.link(mesh_obj)
        mesh_obj.parent = self._armature_obj

        return mesh_obj

    def _merge_armature_meshes(self):
        pose_info: dict[str, Matrix] = {}
        for bone in self._armature_obj.pose.bones:
            pose_info[bone.name] = bone.matrix_basis.copy()
            bone.matrix_basis = Matrix.Identity(4)

        bpy.ops.object.select_all(action='DESELECT')
        for mesh_obj in self._armature_obj.children:
            mesh_obj.select_set(True)

        target_mesh = bpy.data.meshes.new(f"{self._model.name}_Mesh")
        target_mesh_obj = bpy.data.objects.new(target_mesh.name, target_mesh)
        self._collection.objects.link(target_mesh_obj)
        target_mesh_obj.parent = self._armature_obj

        target_mesh_obj.select_set(True)
        self._context.view_layer.objects.active = target_mesh_obj

        bpy.ops.object.join()
        bpy.ops.object.select_all(action='DESELECT')

        armature_modifier: bpy.types.ArmatureModifier = target_mesh_obj.modifiers.new("Armature", 'ARMATURE')
        armature_modifier.object = self._armature_obj

        for bone_name, matrix in pose_info.items():
            bone = self._armature_obj.pose.bones[bone_name]
            bone.matrix_basis = matrix

    #########################################################

    def _align_with_bone_transforms(self, mesh_obj: bpy.types.Object, bone_index: int):

        bone = self._armature_obj.pose.bones[bone_index]
        bone_matrix = self._armature_obj.matrix_world @ bone.matrix

        pos, rot, scale = bone_matrix.decompose()
        mesh_obj.matrix_world = Matrix.LocRotScale(
            pos, rot, Vector((1.0 / scale.x, 1.0 / scale.y, 1.0 / scale.z)))

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

    def _setup_weighted_mesh(self, meshdata: i_mesh.ConvertedMesh):
        mesh_obj = self._create_mesh_object(meshdata.mesh)
        self._align_with_bone_transforms(mesh_obj, meshdata.mesh_info.attached_node_index)
        self._setup_mesh_modifiers(mesh_obj)

    def _setup_unweighted_mesh(self, mesh: i_mesh.ConvertedMesh):
        mesh_obj = self._create_mesh_object(mesh.mesh)

        mesh_obj.parent_type = 'BONE'
        mesh_obj.parent_bone = self._armature.bones[mesh.mesh_info.attached_node_index].name

        self._context.view_layer.update()

        bone = self._armature_obj.pose.bones[mesh_obj.parent_bone]
        bone_matrix = self._armature_obj.matrix_world @ bone.matrix

        mesh_obj.matrix_parent_inverse = (
            mesh_obj.matrix_world.inverted() @ bone_matrix
        )

    #########################################################

    def _convert_nodes_to_armature(self):

        self._setup_armature()

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        self._create_bones()
        self._correct_bone_lengths()

        bpy.ops.object.mode_set(mode='OBJECT')

        self._pre_bone_scale_correct()

        for mesh in self._meshes:
            if mesh.has_weights:
                self._setup_weighted_mesh(mesh)
            else:
                self._setup_unweighted_mesh(mesh)

        self._post_bone_scale_correct()

        if self._merge_meshes:
            self._merge_armature_meshes()

        return self._armature_obj

    #########################################################

    def convert_model(self, collection: bpy.types.Collection, model: CModel):
        self._model = model
        self._collection = collection
        self._c_nodes: list[CNode] = [model.nodes[i] for i in range(model.nodes_size)]

        if model.nodes_size > 1:
            self._node_names = [
                f"{i:03d}_{node.label}" if self._ensure_order else node.label
                for i, node in enumerate(self._c_nodes)
            ]
        else:
            self._node_names = [self._c_nodes[0].label]

        c_meshes: list[CMeshConversionInfo] = [model.meshes[i] for i in range(model.meshes_size)]

        convert_to_objects = not self._force_armature

        if not convert_to_objects and model.nodes_size == 1:
            convert_to_objects = True

        if convert_to_objects:
            has_weights = any([c_mesh.mesh.weight_node_index_map_size > 0 for c_mesh in c_meshes])
            attached_node_indices = [c_mesh.attached_node_index for c_mesh in c_meshes]
            has_shared_node_meshes = len(set(attached_node_indices)) < len(attached_node_indices)
            has_root_siblings = len([node for node in self._c_nodes if node.parent_index == -1]) > 1

            if has_weights or has_shared_node_meshes or has_root_siblings:
                convert_to_objects = False

        self._meshes = self._mesh_converter.convert_meshes(
            model.name,
            self._node_names,
            not convert_to_objects,
            c_meshes
        )

        if convert_to_objects:
            result = self._convert_nodes_to_objects()
        else:
            result = self._convert_nodes_to_armature()

        return result

    def reset(self):
        self._mesh_converter.reset()