import bpy

from . import i_enum
from .i_mesh import MeshData
from .i_node import NodeProcessor
from .i_motion import NodeMotionProcessor

from ..dotnet import SAIO_NET



class LandtableProcessor:

    _context: bpy.types.Context
    _optimize: bool
    _ensure_static_order: bool

    _merge_anim_meshes: bool
    _ensure_anim_order: bool

    _rotation_mode: bool
    _quaternion_threshold: bool
    _short_rot: bool

    _import_data: any
    _landtable: any
    _name: str

    _collection: bpy.types.Collection
    _visual_collection: bpy.types.Collection
    _collision_collection: bpy.types.Collection
    _hybrid_collection: bpy.types.Collection | None
    _neither_collection: bpy.types.Collection | None

    _animation_collection: bpy.types.Collection | None
    _motion_lut: dict[any, bpy.types.Action]

    _meshes: list[MeshData]

    def __init__(
            self,
            context: bpy.types.Context,
            optimize: bool,
            ensure_entry_order: bool,
            merge_anim_meshes: bool,
            ensure_anim_order: bool,
            rotation_mode: bool,
            quaternion_threshold: bool,
            short_rot: bool):

        self._context = context
        self._optimize = optimize
        self._ensure_static_order = ensure_entry_order

        self._merge_anim_meshes = merge_anim_meshes
        self._ensure_anim_order = ensure_anim_order

        self._rotation_mode = rotation_mode
        self._quaternion_threshold = quaternion_threshold
        self._short_rot = short_rot

        self._motion_lut = dict()

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

        if self._import_data.LandTable.GeometryAnimations.Length > 0:
            self._animation_collection = bpy.data.collections.new(
                self._name + "_animated")
            self._collection.children.link(self._animation_collection)
        else:
            self._animation_collection = None

    def _process_meshes(self):
        from .i_mesh import MeshProcessor

        self._meshes = MeshProcessor.process_meshes(
            self._context,
            self._import_data.Attaches,
            self._name)

    def _setup_object(self, landentry, index):
        from . import i_matrix

        mesh_data = self._meshes[landentry.MeshIndex]

        if self._ensure_static_order:
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

    def _process_nodemotion(self, motion):
        model_data = SAIO_NET.MODEL.Process(
            motion.Model,
            self._optimize
        )

        node_lut = {}

        obj = NodeProcessor.process_model(
            self._context,
            model_data,
            self._animation_collection,
            motion.NodeMotion.Label,
            motion.NodeMotion.Label,
            node_lut,
            motion.Model.Child is not None or motion.Model.Next is not None,
            self._merge_anim_meshes,
            self._ensure_anim_order
        )

        le_prop = obj.saio_land_entry

        le_prop.geometry_type = 'ANIMATED'
        le_prop.anim_start_frame = motion.Frame
        le_prop.anim_speed = motion.Step
        le_prop.tex_list_pointer =  f"{motion.TextureListPointer:08X}"

        if obj.type == 'ARMATURE':
            action = NodeMotionProcessor.process_motion(
                motion.NodeMotion.Animation,
                obj,
                self._rotation_mode,
                self._quaternion_threshold)

        elif motion.NodeMotion.Animation in self._motion_lut:
            action = self._motion_lut[motion.NodeMotion.Animation]

        else:
            action = NodeMotionProcessor.process_motion(
                motion.NodeMotion.Animation,
                obj,
                self._rotation_mode,
                self._quaternion_threshold)

            self._motion_lut[motion.NodeMotion.Animation] = action

        anim_data = obj.animation_data_create()
        anim_data.action = action

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

        for motion in self._import_data.LandTable.GeometryAnimations:
            self._process_nodemotion(motion)

        if len(self._neither_collection.objects) == 0:
            bpy.data.collections.remove(
                self._neither_collection, do_unlink=True)
            self._neither_collection = None

        if len(self._hybrid_collection.objects) == 0:
            bpy.data.collections.remove(
                self._hybrid_collection, do_unlink=True)
            self._hybrid_collection = None

    @staticmethod
    def process_landtable(
            context: bpy.types.Context,
            import_data,
            name: str,
            optimize: bool,
            ensure_entry_order: bool,
            merge_anim_meshes: bool,
            ensure_anim_order: bool,
            rotation_mode: bool,
            quaternion_threshold: bool,
            short_rot: bool):

        processor = LandtableProcessor(
            context,
            optimize,
            ensure_entry_order,
            merge_anim_meshes,
            ensure_anim_order,
            rotation_mode,
            quaternion_threshold,
            short_rot)

        processor.process(import_data, name)
