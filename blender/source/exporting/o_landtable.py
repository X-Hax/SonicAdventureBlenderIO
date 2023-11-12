import bpy
from . import o_enum, o_matrix, o_mesh
from ..dotnet import SAIO_NET

class LandtableEvaluator:

    _context: bpy.types.Context
    _format: str
    _optimize: bool
    _write_specular: bool
    _apply_modifs: bool
    _fallback_surface_attributes: bool
    _automatic_node_attributes: bool

    _mesh_lut: dict[bpy.types.Object | bpy.types.Mesh, int]
    _land_entries: list
    _temp_objects: list[bpy.types.Object]
    _modelmeshes: list[o_mesh.ModelMesh]
    _mesh_structs: list

    def __init__(
            self,
            context: bpy.types.Context,
            format: str,
            optimize: bool = True,
            write_specular: bool = True,
            apply_modifs: bool = True,
            fallback_surface_attributes: bool = True,
            automatic_node_attributes: bool = True):

        self._context = context
        self._format = format
        self._optimize = optimize
        self._write_specular = write_specular
        self._apply_modifs = apply_modifs
        self._fallback_surface_attributes = fallback_surface_attributes
        self._automatic_node_attributes = automatic_node_attributes

        self._mesh_lut = {}
        self._land_entries = []
        self._temp_objects = []
        self._modelmeshes = []
        self._mesh_structs = None

    def _setup(self):
        self._mesh_lut.clear()
        self._land_entries.clear()
        self._temp_objects.clear()
        self._modelmeshes.clear()
        self._mesh_structs = None

    def _eval_mesh_index(self, object: bpy.types.Object):
        if len(object.modifiers) > 0 and self._apply_modifs:
            mesh_index = len(self._mesh_lut)
            self._mesh_lut[object] = mesh_index

        elif object.data in self._mesh_lut:
            mesh_index = self._mesh_lut[object.data]

        else:
            mesh_index = len(self._mesh_lut)
            self._mesh_lut[object.data] = mesh_index

        return mesh_index

    def _eval_entry(self, object: bpy.types.Object):
        mesh_index = self._eval_mesh_index(object)

        surface_attributes = o_enum.to_surface_attributes(
            object.saio_land_entry)

        node_attributes = o_enum.to_node_attributes(
            object.saio_node)

        mtx = o_matrix.bpy_to_net_matrix(object.matrix_world)

        landentry = SAIO_NET.LAND_ENTRY_STRUCT(
            object.name,
            mesh_index,
            node_attributes,
            surface_attributes,
            mtx
        )

        self._land_entries.append(landentry)

    def _eval_mesh_models(self):
        for mesh in self._mesh_lut.keys():
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
            self._context, self._modelmeshes, True)

    def _cleanup(self):
        for temp in self._temp_objects:
            bpy.data.objects.remove(temp)

    def evaluate(self, objects: list[bpy.types.Object]):

        self._setup()

        for obj in objects:
            if obj.type == 'MESH' and len(obj.data.polygons) > 0:
                self._eval_entry(obj)

        self._eval_mesh_models()
        self._cleanup()

    def export(self, filepath: str):
        model_format = o_enum.to_model_format(self._format)
        landtable_prop = self._context.scene.saio_scene.landtable
        texlist_pointer = int(landtable_prop.tex_list_pointer, base=16)

        SAIO_NET.LANDTABLE_WRAPPER.Export(
            self._land_entries,
            self._mesh_structs,
            model_format,

            landtable_prop.name,
            landtable_prop.draw_distance,
            landtable_prop.tex_file_name,
            texlist_pointer,

            filepath,
            self._optimize,
            self._write_specular,
            self._fallback_surface_attributes,
            self._automatic_node_attributes,
            self._context.scene.saio_scene.author,
            self._context.scene.saio_scene.description)
