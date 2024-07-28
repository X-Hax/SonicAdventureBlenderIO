import bpy

from . import o_enum, o_matrix, o_mesh, o_motion
from .o_model import ModelEvaluator

from ..dotnet import SAIO_NET, SA3D_Modeling
from ..utility import general
from ..utility.anim_parameters import AnimParameters
from ..exceptions import UserException


class LandtableEvaluator:

    _context: bpy.types.Context
    _format: str
    _model_format: str
    _optimize: bool
    _write_specular: bool
    _apply_modifs: bool
    _fallback_surface_attributes: bool
    _auto_node_attribute_mode: any

    _auto_root: bool
    _force_sort_bones: bool
    _anim_parameters: AnimParameters

    _le_objects: set[bpy.types.Object]
    _anim_objects: list[set[bpy.types.Object]]

    _mesh_lut: dict[bpy.types.Object | bpy.types.Mesh, int]
    _land_entries: list
    _temp_objects: list[bpy.types.Object]
    _modelmeshes: list[o_mesh.ModelMesh]
    _mesh_structs: list
    _motion_lut: dict[bpy.types.Action, any]
    _motions: list

    def __init__(
            self,
            context: bpy.types.Context,
            model_format: str,
            optimize: bool,
            write_specular: bool,
            apply_modifs: bool,
            fallback_surface_attributes: bool,
            auto_node_attribute_mode: bool,
            auto_root: bool,
            force_sort_bones: bool,
            anim_parameters: AnimParameters):

        self._context = context
        self._format = model_format
        self._model_format = o_enum.to_model_format(model_format)
        self._optimize = optimize
        self._write_specular = write_specular
        self._apply_modifs = apply_modifs
        self._fallback_surface_attributes = fallback_surface_attributes
        self._auto_node_attribute_mode = o_enum.to_auto_node_attribute_mode(auto_node_attribute_mode)

        self._auto_root = auto_root
        self._force_sort_bones = force_sort_bones
        self._anim_parameters = anim_parameters

        self._le_objects = set()
        self._anim_objects = list()

        self._mesh_lut = {}
        self._land_entries = []
        self._temp_objects = []
        self._modelmeshes = []
        self._mesh_structs = None
        self._motion_lut = {}
        self._motions = []

    def _setup(self):
        self._mesh_lut.clear()
        self._land_entries.clear()
        self._temp_objects.clear()
        self._modelmeshes.clear()
        self._mesh_structs = None

    def _organize_objects(self, objects: set[bpy.types.Object]):
        root_dict: dict[bpy.types.Object, set[bpy.types.Object]] = dict()

        for obj in objects:
            parent = obj
            while parent.parent is not None:
                parent = parent.parent

            if parent not in root_dict:
                obj_set = set()
                root_dict[parent] = obj_set
            else:
                obj_set = root_dict[parent]

            obj_set.add(obj)

        for root, root_objects in root_dict.items():
            if root.type == 'ARMATURE' or (
                    root.type == 'MESH'
                    and len(root.children) == 0
                    and root.saio_land_entry.geometry_type == 'ANIMATED'):

                root_objects.add(root)  # just to be sure
                self._anim_objects.append(root_objects)
            else:
                self._le_objects.update(root_objects)

    def _eval_mesh_index(self, obj: bpy.types.Object):
        if len(obj.modifiers) > 0 and self._apply_modifs:
            mesh_index = len(self._mesh_lut)
            self._mesh_lut[obj] = mesh_index

        elif obj.data in self._mesh_lut:
            mesh_index = self._mesh_lut[obj.data]

        else:
            mesh_index = len(self._mesh_lut)
            self._mesh_lut[obj.data] = mesh_index

        return mesh_index

    def _eval_entry(self, obj: bpy.types.Object):
        mesh_index = self._eval_mesh_index(obj)
        blockbit = int(obj.saio_land_entry.blockbit, base=16)

        surface_attributes = o_enum.to_surface_attributes(
            obj.saio_land_entry)

        node_attributes = o_enum.to_node_attributes(
            obj.saio_node)

        mtx = o_matrix.bpy_to_net_matrix(obj.matrix_world)

        landentry = SAIO_NET.LAND_ENTRY_STRUCT(
            general.remove_digit_prefix(obj.name),
            mesh_index,
            blockbit,
            node_attributes,
            surface_attributes,
            mtx
        )

        self._land_entries.append(landentry)

    def _eval_mesh_models(self):
        for mesh in self._mesh_lut:
            mesh_obj = mesh
            if not isinstance(mesh, bpy.types.Object):
                mesh_obj = bpy.data.objects.new("##TEMP##", mesh)
                self._temp_objects.append(mesh_obj)

                # we need to add the temporary object to the view layer,
                # otherwise the mesh wont get correctly evaluated
                (self._context
                     .view_layer
                     .layer_collection
                     .collection
                     .objects).link(mesh_obj)

            model = o_mesh.ModelMesh(None, mesh_obj, None, None)
            self._modelmeshes.append(model)

        # we apply modifiers here since the only models with modifiers
        # are those that we added before based on whether we apply modifiers
        self._mesh_structs = o_mesh.ModelMesh.evaluate_models(
            self._context, self._modelmeshes, True, False)

    def _cleanup(self):
        for temp in self._temp_objects:
            bpy.data.objects.remove(temp)

    def _eval_animated(self, objects: set[bpy.types.Object]):

        root = None
        for obj in objects:
            if obj.parent is None:
                root = obj
                break

        if root.animation_data is None:
            raise UserException((
                f"Object \"{root.name}\" was identified as"
                " animated geometry but has no animation data!"))

        if root.animation_data.action is None:
            raise UserException((
                f"Object \"{root.name}\" was identified as"
                " animated geometry but has no active action!"))

        evaluator = ModelEvaluator(
            self._context,
            self._format,
            self._auto_root,
            self._optimize,
            self._write_specular,
            self._apply_modifs,
            False,  # Dont apply posing
            self._auto_node_attribute_mode,
            self._force_sort_bones,
            False)  # Dont flip vertex colors

        modeldata = evaluator.evaluate(objects)

        action = root.animation_data.action

        if action in self._motion_lut:
            motion = self._motion_lut[action]
        else:
            motion = o_motion.convert_to_node_motion(
                root,
                self._force_sort_bones,
                action.fcurves,
                action.frame_range,
                action.name,
                self._anim_parameters
            )

            self._motion_lut[action] = motion

        lem = SA3D_Modeling.LAND_ENTRY_MOTION(
            root.saio_land_entry.anim_start_frame,
            root.saio_land_entry.anim_speed,
            motion.GetFrameCount(),
            modeldata.outdata,
            motion,
            int(root.saio_land_entry.tex_list_pointer, base=16))

        self._motions.append(lem)

    def evaluate(self, objects: set[bpy.types.Object]):

        self._setup()
        self._organize_objects(objects)

        for anim_tree in self._anim_objects:
            self._eval_animated(anim_tree)

        for obj in sorted(self._le_objects, key=lambda x: x.name.lower()):
            if obj.type == 'MESH' and len(obj.data.polygons) > 0:
                self._eval_entry(obj)

        self._eval_mesh_models()
        self._cleanup()

    def save_debug(self, filepath: str):
        landtable_prop = self._context.scene.saio_scene.landtable
        texlist_pointer = int(landtable_prop.tex_list_pointer, base=16)

        SAIO_NET.DEBUG_LEVEL(
            self._land_entries,
            self._mesh_structs,
            self._motions,
            self._model_format,

            landtable_prop.name,
            landtable_prop.draw_distance,
            landtable_prop.tex_file_name,
            texlist_pointer,

            filepath,
            self._optimize,
            self._write_specular,
            self._fallback_surface_attributes,
            self._auto_node_attribute_mode,
            self._anim_parameters.ensure_positive_euler_angles,
            self._context.scene.saio_scene.author,
            self._context.scene.saio_scene.description
        ).ToFile(filepath)

    def export(self, filepath: str):
        landtable_prop = self._context.scene.saio_scene.landtable
        texlist_pointer = int(landtable_prop.tex_list_pointer, base=16)

        SAIO_NET.LANDTABLE_WRAPPER.Export(
            self._land_entries,
            self._mesh_structs,
            self._motions,
            self._model_format,

            landtable_prop.name,
            landtable_prop.draw_distance,
            landtable_prop.tex_file_name,
            texlist_pointer,

            filepath,
            self._optimize,
            self._write_specular,
            self._fallback_surface_attributes,
            self._auto_node_attribute_mode,
            self._anim_parameters.ensure_positive_euler_angles,
            self._context.scene.saio_scene.author,
            self._context.scene.saio_scene.description)
