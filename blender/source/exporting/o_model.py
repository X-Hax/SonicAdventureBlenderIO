import bpy

from . import o_node, o_enum
from .o_mesh import ModelMesh

from ..dotnet import SAIO_NET


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
        for obj, matrix in self.node_data.weighted_models:
            model = ModelMesh(
                self.node_data,
                obj,
                matrix,
                None)

            self.meshes[obj] = model

        for attached_node_name, virtual_objects \
                in self.node_data.bone_models.items():

            for obj, matrix in virtual_objects:
                model = ModelMesh(
                    self.node_data,
                    obj,
                    matrix,
                    attached_node_name)

                self.meshes[obj] = model

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
    _attach_format: str
    _auto_root: bool
    _optimize: bool
    _write_specular: bool
    _apply_modifs: bool
    _apply_pose: bool
    _automatic_node_attributes: bool
    _force_sort_bones: bool
    _flip_vertex_color_channels: bool
    _node_evaluator: o_node.NodeEvaluator

    _output: ModelData

    def __init__(
            self,
            context: bpy.types.Context,
            attach_format: str,
            auto_root: bool = True,
            optimize: bool = True,
            write_specular: bool = True,
            apply_modifs: bool = True,
            apply_pose: bool = False,
            automatic_node_attributes: bool = True,
            force_sort_bones: bool = False,
            flip_vertex_color_channels: bool = False,):

        self._context = context
        self._attach_format = attach_format
        self._auto_root = auto_root
        self._optimize = optimize
        self._write_specular = write_specular
        self._apply_modifs = apply_modifs
        self._apply_pose = apply_pose
        self._automatic_node_attributes = automatic_node_attributes
        self._flip_vertex_color_channels = flip_vertex_color_channels
        self._node_evaluator = o_node.NodeEvaluator(
            context, self._auto_root, True, apply_pose, force_sort_bones)

        self._output = None

    def _setup(self):
        self._output = ModelData()

    def _eval_nodes(self, objects: set[bpy.types.Object]):
        self._output.node_data = self._node_evaluator.evaluate(objects)

    def _eval_mesh_structures(self, convert: bool):
        self._output.mesh_structs = ModelMesh.evaluate_models(
            self._context,
            self._output.meshes.values(),
            self._apply_modifs,
            self._apply_pose,
            convert)

    def _convert_structures(self):
        self._output.outdata = SAIO_NET.MODEL.ToNodeStructure(
            self._output.node_data.nodes,
            self._output.mesh_structs,
            self._output.attach_format,
            self._optimize,
            self._write_specular,
            self._automatic_node_attributes,
            self._flip_vertex_color_channels)

    def save_debug(self, filepath: str):
        SAIO_NET.DEBUG_MODEL(
            self._output.node_data.nodes,
            self._output.mesh_structs,
            self._output.attach_format,
            self._optimize,
            self._write_specular,
            self._automatic_node_attributes,
            self._flip_vertex_color_channels
        ).ToFile(filepath)

    def evaluate(self, objects: set[bpy.types.Object], convert: bool = True):
        self._setup()
        self._eval_nodes(objects)
        self._output.eval_modelmeshes()
        self._eval_mesh_structures(convert)

        if convert:
            self._output.attach_format = o_enum.to_attach_format(
                self._attach_format)
            self._convert_structures()

        return self._output
