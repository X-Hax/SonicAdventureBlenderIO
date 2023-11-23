import bpy

from . import i_enum
from .i_mesh import MeshData


class LandtableProcessor:

    _context: bpy.types.Context
    _optimize: bool

    _import_data: any
    _landtable: any
    _name: str

    _collection: bpy.types.Collection
    _visual_collection: bpy.types.Collection
    _collision_collection: bpy.types.Collection

    _meshes: list[MeshData]

    def __init__(
            self,
            context: bpy.types.Context,
            optimize: bool):
        self._context = context
        self._optimize = optimize

    def _get_string(self, value) -> str:
        if value is None:
            return ""
        return value

    def _setup_scene(self):
        scene = self._context.scene

        scene.saio_scene.scene_type = "LVL"

        landtable_prop = scene.saio_scene.landtable
        landtable_prop.draw_distance = self._landtable.DrawDistance
        landtable_prop.name = self._landtable.Label

        scene.saio_scene.author = self._get_string(
            self._import_data.MetaData.Author)

        scene.saio_scene.description = self._get_string(
            self._import_data.MetaData.Description)

        landtable_prop.tex_file_name = self._get_string(
            self._landtable.TextureFileName)

        landtable_prop.tex_list_pointer \
            = f"{self._landtable.TexListPtr:08X}"

    def _setup_collections(self):
        self._collection = bpy.data.collections.new(self._name)
        self._context.scene.collection.children.link(self._collection)

        self._visual_collection = bpy.data.collections.new(
            self._name + "_visual")
        self._collection.children.link(self._visual_collection)

        self._collision_collection = bpy.data.collections.new(
            self._name + "_collision")
        self._collection.children.link(self._collision_collection)

    def _process_meshes(self):
        from .i_mesh import MeshProcessor

        self._meshes = MeshProcessor.process_meshes(
            self._context,
            self._import_data.Attaches,
            self._name)

    def _setup_object(self, landentry):
        from . import i_matrix

        mesh_data = self._meshes[landentry.MeshIndex]
        obj = bpy.data.objects.new(landentry.Label, mesh_data.mesh)

        obj.saio_land_entry.blockbit = f"{landentry.BlockBit:08X}"
        obj.saio_land_entry.sf_visible = False

        i_enum.from_surface_attributes(
            landentry.SurfaceAttributes, obj.saio_land_entry)

        i_enum.from_node_attributes(
            obj.saio_node, landentry.NodeAttributes)

        obj.matrix_world = i_matrix.net_to_bpy_matrix(
            landentry.WorldMatrix)

        return obj

    def _assign_collection(self, index: int, obj: bpy.types.Object):
        if self._import_data.VisualCount is not None:
            is_visual = index < self._import_data.VisualCount
            is_collision = not is_visual
        else:
            is_visual = obj.saio_land_entry.is_visual
            is_collision = obj.saio_land_entry.is_collision

        if is_visual:
            self._visual_collection.objects.link(obj)

        if is_collision:
            self._collision_collection.objects.link(obj)

        if not is_visual and not is_collision:
            self._collection.objects.link(obj)

    def process(self, import_data, name: str):

        self._import_data = import_data
        self._landtable = import_data.LandTable
        self._name = name

        self._setup_scene()
        self._setup_collections()
        self._process_meshes()

        for index, landentry in enumerate(self._import_data.LandEntries):
            obj = self._setup_object(landentry)
            self._assign_collection(index, obj)

    @staticmethod
    def process_landtable(
            context: bpy.types.Context,
            import_data,
            name: str,
            optimize: bool):

        processor = LandtableProcessor(context, optimize)
        processor.process(import_data, name)
