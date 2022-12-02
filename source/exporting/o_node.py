import bpy
from bpy.types import Object as BObject, PoseBone
from mathutils import Matrix

VIRTUAL_MODELS = list[tuple[BObject, Matrix]]


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

    weighted_models: VIRTUAL_MODELS
    '''Armature children that are deformed with weights'''

    bone_models: dict[str, VIRTUAL_MODELS]
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
            from SA3D.Modeling.Blender import Flags
            node_attributes = Flags.ComposeNodeAttributes(
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

        from SA3D.Modeling.Blender import NodeStruct

        self.nodes.append(NodeStruct(
            node_name,
            parent_index,
            node_attributes,
            net_mtx))

    def add_virtual_model(self, object: BObject):
        root_parent = object
        while object.parent is not self.armature_object:
            root_parent = object.parent

        bone_name = None
        if root_parent.parent_type == 'BONE':
            bone_name = root_parent.parent_bone
        elif root_parent != object or not any(
                [x.type == 'ARMATURE' for x in object.modifiers]):
            bone_name = self.root_bone_name

        result = (object, object.matrix_world.copy())

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

    _legacy_hierarchy: bool
    '''Evaluate an armatures object as its root node'''

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
            correct_names: bool,
            apply_pose: bool,
            force_sort_bones: bool):

        self._context = context
        self._correct_names = correct_names
        self._apply_pose = apply_pose
        self.force_sort = force_sort_bones

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

        underscore = name.find("_")
        if underscore == -1:
            return name

        for i in range(underscore):
            if not name[i].isdigit():
                return name

        return name[underscore+1:]

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

    def _evaluate_object_tree(self, objects: list[BObject]):
        '''Compiles an object hierarchy of the passed objects'''
        self._parentless.clear()
        self._hierarchy_dictionary.clear()

        for object in objects:

            parent = object.parent
            while parent is not None and parent not in objects:
                parent = parent.parent

            if parent is not None:
                if parent not in self._hierarchy_dictionary:
                    self._hierarchy_dictionary[parent] = [object]
                else:
                    self._hierarchy_dictionary[parent].append(object)
            else:
                self._parentless.append(object)

            if object not in self._hierarchy_dictionary:
                self._hierarchy_dictionary[object] = []

        for objects in self._hierarchy_dictionary.values():
            objects.sort(key=lambda x: x.name)

        self._parentless.sort(key=lambda x: x.name)

    def _eval_object(self, object: BObject, parent_index: int):

        index = self._node_count
        self._create_node(object, parent_index)

        for child in self._hierarchy_dictionary[object]:
            self._eval_object(child, index)

    ################################################################

    def _eval_bone(self, bone: PoseBone, parent_index: int):

        index = self._node_count
        self._create_node(bone, parent_index)

        children = list(bone.children)

        if self.force_sort:
            children.sort(key=lambda x: x.name)

        for child in children:
            self._eval_bone(child, index)

    def _eval_armature_child(self, object: BObject):
        # Only adding meshes
        if object.type == 'MESH' and len(object.data.polygons) > 0:
            self._output.add_virtual_model(object)

        for child in self._hierarchy_dictionary[object]:
            self._eval_armature_child(child)

    def _eval_armature(self, object: BObject):

        if len(object.data.bones) == 0:
            raise Exception("Armature has no bones")

        self._output.armature_object = object

        if not self._apply_pose:
            prev_pose_position = object.data.pose_position
            object.data.pose_position = 'REST'
            self._context.view_layer.update()

        parentless_bones = [
            bone for bone in object.pose.bones
            if bone.parent is None]

        parent_index = -1
        if len(parentless_bones) > 1:
            parent_index = 0
            self._create_root_node()

        for bone in parentless_bones:
            self._eval_bone(bone, parent_index)

        for child in self._hierarchy_dictionary[object]:
            self._eval_armature_child(child)

        if not self._apply_pose:
            object.data.pose_position = prev_pose_position
            self._context.view_layer.update()

    ################################################################

    def evaluate(self, objects: list[BObject]):

        from ..utility import dll_utils
        dll_utils.load_library()

        if len(objects) == 0:
            raise Exception("No objects to export")

        self._setup()
        self._evaluate_object_tree(objects)
        self._base_matrix = Matrix.Identity(4)

        if len(self._parentless) > 1:
            self._create_root_node()
            for parentless in self._parentless:
                self._eval_object(parentless, 0)
        else:
            parentless = self._parentless[0]
            if parentless.type == 'ARMATURE':
                self._base_matrix = parentless.matrix_world
                self._eval_armature(parentless)
            else:
                self._eval_object(parentless, -1)

        return self._output
