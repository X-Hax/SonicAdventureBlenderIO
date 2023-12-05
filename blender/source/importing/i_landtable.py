import bpy

from . import i_enum
from .i_mesh import MeshData


class LandtableProcessor:

    _context: bpy.types.Context
    _optimize: bool
    _ensure_entry_order: bool

    _import_data: any
    _landtable: any
    _name: str

    _collection: bpy.types.Collection
    _visual_collection: bpy.types.Collection
    _collision_collection: bpy.types.Collection
    _hybrid_collection: bpy.types.Collection | None
    _neither_collection: bpy.types.Collection | None

    _meshes: list[MeshData]

    def __init__(
            self,
            context: bpy.types.Context,
            optimize: bool,
            ensure_entry_order: bool):
        self._context = context
        self._optimize = optimize
        self._ensure_entry_order = ensure_entry_order

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

        self._hybrid_collection = bpy.data.collections.new(
            self._name + "_hybrid")
        self._collection.children.link(self._hybrid_collection)

        self._neither_collection = bpy.data.collections.new(
            self._name + "_neither")
        self._collection.children.link(self._neither_collection)

    def _process_meshes(self):
        from .i_mesh import MeshProcessor

        self._meshes = MeshProcessor.process_meshes(
            self._context,
            self._import_data.Attaches,
            self._name)

    def _setup_object(self, landentry, index):
        from . import i_matrix

        mesh_data = self._meshes[landentry.MeshIndex]

        if self._ensure_entry_order:
            label = f"{index:04}_{landentry.Label}"
        else:
            label = landentry.Label

        obj = bpy.data.objects.new(label, mesh_data.mesh)

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

        if is_visual and is_collision:
            self._hybrid_collection.objects.link(obj)

        elif is_visual:
            self._visual_collection.objects.link(obj)

        elif is_collision:
            self._collision_collection.objects.link(obj)

        else:
            self._neither_collection.objects.link(obj)

    def process(self, import_data, name: str):

        self._import_data = import_data
        self._landtable = import_data.LandTable
        self._name = name

        self._setup_scene()
        self._setup_collections()
        self._process_meshes()

        for index, landentry in enumerate(self._import_data.LandEntries):
            obj = self._setup_object(landentry, index)
            self._assign_collection(index, obj)

        if len(self._neither_collection.objects) == 0:
            bpy.data.collections.remove(self._neither_collection, do_unlink=True)
            self._neither_collection = None

        if len(self._hybrid_collection.objects) == 0:
            bpy.data.collections.remove(self._hybrid_collection, do_unlink=True)
            self._hybrid_collection = None

    @staticmethod
    def process_landtable(
            context: bpy.types.Context,
            import_data,
            name: str,
            optimize: bool,
            ensure_entry_order: bool):

        processor = LandtableProcessor(context, optimize, ensure_entry_order)
        processor.process(import_data, name)
