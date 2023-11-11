import bpy

from . import o_node, o_enum
from .o_mesh import ModelMesh


class ModelData:

    node_data: o_node.NodeStructure
    meshes: dict[bpy.types.Object, ModelMesh]
    mesh_structs: list
    attach_format: any
    outdata: any

    def __init__(self):
        self.node_data = None
        self.meshes = {}
        self.mesh_structs = []
        self.attach_format = None
        self.outdata = None

    def _eval_armature_meshes(self):
        for object, matrix in self.node_data.weighted_models:
            model = ModelMesh(
                self.node_data,
                object,
                matrix,
                None)

            self.meshes[object] = model

        for attached_node_name, virtual_objects \
                in self.node_data.bone_models.items():

            for object, matrix in virtual_objects:
                model = ModelMesh(
                    self.node_data,
                    object,
                    matrix,
                    attached_node_name)

                self.meshes[object] = model

    def _eval_object_meshes(self):
        for node in self.node_data.node_mapping.keys():
            if (node is None
                    or node.type != 'MESH'
                    or len(node.data.vertices) == 0):
                continue

            model = ModelMesh(
                self.node_data,
                node,
                node.matrix_world.copy(),
                node.name)

            self.meshes[node] = model

    def eval_modelmeshes(self):
        if self.node_data.armature_object is not None:
            self._eval_armature_meshes()
        else:
            self._eval_object_meshes()


class ModelEvaluator:

    _context: bpy.types.Context
    _format: str
    _auto_root: bool
    _optimize: bool
    _ignore_weights: bool
    _write_specular: bool
    _apply_modifs: bool
    _automatic_node_attributes: bool
    _force_sort_bones: bool
    _node_evaluator: o_node.NodeEvaluator

    _output: ModelData

    def __init__(
            self,
            context: bpy.types.Context,
            format: str,
            auto_root: bool = True,
            optimize: bool = True,
            ignore_weights: bool = False,
            write_specular: bool = True,
            apply_modifs: bool = True,
            apply_pose: bool = False,
            automatic_node_attributes: bool = True,
            force_sort_bones: bool = False):

        self._context = context
        self._format = format
        self._auto_root = auto_root
        self._optimize = optimize
        self._ignore_weights = ignore_weights
        self._write_specular = write_specular
        self._apply_modifs = apply_modifs
        self._automatic_node_attributes = automatic_node_attributes
        self._node_evaluator = o_node.NodeEvaluator(
            context, True, apply_pose, force_sort_bones)

        self._output = None

    @property
    def _ignore_root(self):
        return (
            not self._auto_root
            and self._output.node_data.has_auto_root
        )

    def _setup(self):
        self._output = ModelData()

    def _eval_nodes(self, objects: list[bpy.types.Object]):
        self._output.node_data = self._node_evaluator.evaluate(objects)

    def _eval_mesh_structures(self, convert: bool):
        self._output.mesh_structs = ModelMesh.evaluate_models(
            self._context,
            self._output.meshes.values(),
            self._apply_modifs,
            convert)

    def _convert_structures(self):
        from SA3D.Modeling.Blender import Model

        self._output.outdata = Model.ToNodeStructure(
            self._output.node_data.nodes,
            self._output.mesh_structs,
            self._output.attach_format,
            self._optimize,
            self._ignore_weights,
            self._ignore_root,
            self._write_specular,
            self._automatic_node_attributes)

    def save_debug(self, filepath: str):
        from SA3D.Modeling.Blender import DebugModel
        DebugModel(
            self._output.node_data.nodes,
            self._output.mesh_structs,
            self._output.attach_format,
            self._optimize,
            self._ignore_weights,
            self._ignore_root,
            self._write_specular,
            self._automatic_node_attributes
        ).ToFile(filepath)

    def evaluate(self, objects: list[bpy.types.Object], convert: bool = True):
        self._setup()
        self._eval_nodes(objects)
        self._output.eval_modelmeshes()
        self._eval_mesh_structures(convert)

        if convert:
            self._output.attach_format = o_enum.to_attach_format(self._format)
            self._convert_structures()

        return self._output