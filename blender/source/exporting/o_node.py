import bpy
from bpy.types import Object as BObject, PoseBone
from mathutils import Matrix

from ..dotnet import SAIO_NET
from ..utility import general
from ..exceptions import SAIOException, UserException

VirtualModels = list[tuple[BObject, Matrix]]


class NodeStructure:

    armature_object: BObject
    '''Armature object containing the bones'''

    root_bone_name: str | None
    '''Name of the root bone. None indicates automatic root'''

    nodes: list
    '''Node structs ready for export'''

    node_mapping: dict[BObject | PoseBone, int]
    '''Object/Bone -> node index'''

    node_matrices: dict[str, Matrix]
    '''Source Node name -> Node world matrix'''

    name_mapping: dict[str, int]
    '''Source Node name -> node index (used for weights and root indices)'''

    weighted_models: VirtualModels
    '''Armature children that are deformed with weights'''

    bone_models: dict[str, VirtualModels]
    '''Armature children that are parented to bones //
    [name] = (object, vertex matrix)'''

    def __init__(self):
        self.armature_object = None
        self.root_bone_name = None
        self.nodes = []
        self.node_mapping = {}
        self.node_matrices = {}
        self.name_mapping = {}
        self.weighted_models = []
        self.bone_models = {}

    @property
    def has_auto_root(self):
        return self.root_bone_name is None

    def create_node(
            self,
            source: BObject | PoseBone | None,
            node_name: str,
            base_matrix: Matrix,
            apply_base_matrix: bool,
            parent_index: int):

        if len(self.nodes) == 0 and source is not None:
            self.root_bone_name = source.name

        # fill mappings
        if source is None:
            source_name = None
            matrix = Matrix.Identity(4)
        else:
            source_name = source.name
            if isinstance(source, BObject):
                matrix = source.matrix_world.copy()
            else:
                matrix = source.matrix.copy()

        model_matrix = base_matrix @ matrix

        self.node_mapping[source] = len(self.nodes)
        self.node_matrices[source_name] = model_matrix
        self.name_mapping[source_name] = len(self.nodes)

        # convert node attributes
        if source is None:
            node_attributes = SAIO_NET.FLAGS.ComposeNodeAttributes(
                False, False, False, False, False, False, False, False)
        else:
            from . import o_enum
            if isinstance(source, bpy.types.PoseBone):
                saio_node = source.bone.saio_node
            else:
                saio_node = source.saio_node
            node_attributes = o_enum.to_node_attributes(saio_node)

        # correct the matrix
        from . import o_matrix
        net_mtx = o_matrix.bpy_to_net_matrix(
            model_matrix if apply_base_matrix else matrix)

        self.nodes.append(SAIO_NET.NODE_STRUCT(
            node_name,
            parent_index,
            node_attributes,
            net_mtx))

    def add_virtual_model(self, obj: BObject):
        if obj.parent_type == 'ARMATURE':
            raise UserException(
                f"Object \"{obj.name}\" has parent type armature,"
                " which is not supported by this addon!"
                " Please use the armature modifier instead.")

        root_parent = obj
        while obj.parent is not self.armature_object:
            root_parent = obj.parent

        bone_name = None
        if root_parent.parent_type == 'BONE':
            bone_name = root_parent.parent_bone
        elif root_parent != obj or not any(
                [x.type == 'ARMATURE' for x in obj.modifiers]):
            bone_name = self.root_bone_name

        result = (obj, obj.matrix_world.copy())

        if bone_name is not None:
            if bone_name not in self.bone_models:
                models = []
                self.bone_models[bone_name] = models
            else:
                models = self.bone_models[bone_name]

            models.append(result)
        else:
            self.weighted_models.append(result)


class NodeEvaluator:
    '''Handles node evaluation for objects to export'''

    _context: bpy.types.Context

    _auto_root: bool
    '''Create a root object if there are multiple nodes with no parent'''

    _apply_pose: bool
    '''Keep armature posing on export'''

    _correct_names: bool
    '''Remove the "_###" naming that ensures a kept hierarchy'''

    _force_sort_bones: bool
    '''Blender doesnt sort bones by name, but by its own order.
    This forces bones to be sorted by name'''

    _hierarchy_dictionary: dict[BObject, list[BObject]]
    '''Used objects and their evaluated children'''

    _parentless: list[BObject]
    '''Used objects that do not have any parents in the evaluated hierarchy'''

    _base_matrix: Matrix
    '''Base matrix (World matrix of armature, Identity of objects)'''

    _output: NodeStructure
    '''Output structure'''

    def __init__(
            self,
            context: bpy.types.Context,
            auto_root: bool,
            correct_names: bool,
            apply_pose: bool,
            force_sort_bones: bool):

        self._context = context
        self._auto_root = auto_root
        self._correct_names = correct_names
        self._apply_pose = apply_pose
        self._force_sort_bones = force_sort_bones

        self._hierarchy_dictionary = {}
        self._parentless = []
        self._output = None

    @property
    def _node_count(self):
        return len(self._output.nodes)

    def _setup(self):
        self._parentless.clear()
        self._hierarchy_dictionary.clear()
        self._output = NodeStructure()

    def _correct_name(self, name: str):
        '''Corrects a name to its export counterpart'''

        if not self._correct_names:
            return name
        else:
            return general.remove_digit_prefix(name)

    def _create_root_node(self):
        self._output.create_node(
            None,
            "root",
            self._base_matrix,
            self._apply_pose,
            -1)

    def _create_node(self, source: BObject | PoseBone, parent_index: int):
        self._output.create_node(
            source,
            self._correct_name(source.name),
            self._base_matrix,
            self._apply_pose,
            parent_index)

    ################################################################

    def _evaluate_object_tree(self, objects: set[BObject]):
        '''Compiles an object hierarchy of the passed objects'''
        self._parentless.clear()
        self._hierarchy_dictionary.clear()

        for obj in objects:

            parent = obj.parent
            while parent is not None and parent not in objects:
                parent = parent.parent

            if parent is not None:
                if parent not in self._hierarchy_dictionary:
                    self._hierarchy_dictionary[parent] = [obj]
                else:
                    self._hierarchy_dictionary[parent].append(obj)
            else:
                self._parentless.append(obj)

            if obj not in self._hierarchy_dictionary:
                self._hierarchy_dictionary[obj] = []

        for hierarchy_objects in self._hierarchy_dictionary.values():
            hierarchy_objects.sort(key=lambda x: x.name)

        self._parentless.sort(key=lambda x: x.name)

    def _eval_object(self, obj: BObject, parent_index: int):

        index = self._node_count
        self._create_node(obj, parent_index)

        for child in self._hierarchy_dictionary[obj]:
            self._eval_object(child, index)

    ################################################################

    def _eval_bone(self, bone: PoseBone, parent_index: int):

        index = self._node_count
        self._create_node(bone, parent_index)

        children = list(bone.children)

        if self._force_sort_bones:
            children.sort(key=lambda x: x.name)

        for child in children:
            self._eval_bone(child, index)

    def _eval_armature_child(self, obj: BObject):
        # Only adding meshes
        if obj.type == 'MESH' and len(obj.data.polygons) > 0:
            self._output.add_virtual_model(obj)

        for child in self._hierarchy_dictionary[obj]:
            self._eval_armature_child(child)

    def _eval_armature(self, obj: BObject):

        if len(obj.data.bones) == 0:
            raise SAIOException("Armature has no bones")

        self._output.armature_object = obj

        if not self._apply_pose:
            prev_pose_position = obj.data.pose_position
            obj.data.pose_position = 'REST'
            self._context.view_layer.update()

        parentless_bones = [
            bone for bone in obj.pose.bones
            if bone.parent is None]

        parent_index = -1
        if len(parentless_bones) > 1 and self._auto_root:
            parent_index = 0
            self._create_root_node()

        for bone in parentless_bones:
            self._eval_bone(bone, parent_index)

        for child in self._hierarchy_dictionary[obj]:
            self._eval_armature_child(child)

        if not self._apply_pose:
            obj.data.pose_position = prev_pose_position
            self._context.view_layer.update()

    ################################################################

    def evaluate(self, objects: set[BObject]):

        from ..dotnet import load_dotnet
        load_dotnet()

        if len(objects) == 0:
            raise SAIOException("No objects to export")

        self._setup()
        self._evaluate_object_tree(objects)
        self._base_matrix = Matrix.Identity(4)

        if len(self._parentless) == 1:
            parentless = self._parentless[0]
            if parentless.type == 'ARMATURE':
                self._base_matrix = parentless.matrix_world
                self._eval_armature(parentless)
            else:
                self._eval_object(parentless, -1)

        elif self._auto_root:
            self._create_root_node()
            for parentless in self._parentless:
                self._eval_object(parentless, 0)

        else:
            for parentless in self._parentless:
                self._eval_object(parentless, -1)

        return self._output
