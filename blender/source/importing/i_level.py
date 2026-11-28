import bpy

from . import i_mesh, i_model, i_transform

from ..register.property_groups.level_model_properties import SAIO_LevelModel
from ..external import CLevel, CLevelModel, CMeshConversionInfo

class LevelConverter:
    _context: bpy.types.Context
    _model_converter: i_model.ModelConverter
    _mesh_converter: i_mesh.MeshConverter

    _ensure_static_order: bool

    _level: CLevel | None
    _objects: list[bpy.types.Object] | None

    _collection: bpy.types.Collection
    _visual_collection: bpy.types.Collection
    _collision_collection: bpy.types.Collection
    _hybrid_collection: bpy.types.Collection | None
    _neither_collection: bpy.types.Collection | None

    def __init__(
        self,
        context: bpy.types.Context,
        model_converter: i_model.ModelConverter,
        mesh_converter: i_mesh.MeshConverter,
        ensure_static_order: bool):

        self._context = context
        self._model_converter = model_converter
        self._mesh_converter = mesh_converter

        self._ensure_static_order = ensure_static_order

        self._level = None
        self._objects = None

        self._collection = None
        self._visual_collection = None
        self._collision_collection = None
        self._hybrid_collection = None
        self._neither_collection = None

    def _setup_collections(self):
        name = self._level.name

        self._collection = bpy.data.collections.new(name)
        self._context.scene.collection.children.link(self._collection)

        self._visual_collection = bpy.data.collections.new(name + "_visual")
        self._collection.children.link(self._visual_collection)

        self._collision_collection = bpy.data.collections.new(name + "_collision")
        self._collection.children.link(self._collision_collection)

        self._hybrid_collection = bpy.data.collections.new(name + "_hybrid")
        self._collection.children.link(self._hybrid_collection)

        self._neither_collection = bpy.data.collections.new(name + "_neither")
        self._collection.children.link(self._neither_collection)

    def _cleanup_collections(self):
        if len(self._visual_collection.objects) == 0:
            bpy.data.collections.remove(self._visual_collection, do_unlink=True)
            self._visual_collection = None

        if len(self._collision_collection.objects) == 0:
            bpy.data.collections.remove(self._collision_collection, do_unlink=True)
            self._collision_collection = None

        if len(self._neither_collection.objects) == 0:
            bpy.data.collections.remove(self._neither_collection, do_unlink=True)
            self._neither_collection = None

        if len(self._hybrid_collection.objects) == 0:
            bpy.data.collections.remove(self._hybrid_collection, do_unlink=True)
            self._hybrid_collection = None

    def _setup_meshes(self):
        c_meshes: list[CMeshConversionInfo] = [self._level.meshes[i] for i in range(self._level.meshes_size)]
        
        self._meshes = self._mesh_converter.convert_meshes(
            self._level.name,
            None,
            False,
            c_meshes
        )

        self._mesh_converter.setup_materials(self._context)

    def _setup_object(self, index: int, model: CLevelModel):
        mesh_data = self._meshes[model.mesh_index]

        label = model.node.label
        if self._ensure_static_order:
            label = f"{index:04}_{label}"

        obj = bpy.data.objects.new(label, mesh_data.mesh)
        obj.matrix_world = i_transform.c_to_bpy_matrix(model.node.transform)

        self._model_converter.setup_node_attributes(obj.saio_node, model.node)

        level_model_props: SAIO_LevelModel = obj.saio_level_model
        level_model_props.geometry_type = 'STATIC'
        level_model_props.blockbit = model.blockbit

        if self._level.format == 0: # BASIC
            level_model_props.sa1_surface_attributes = model.surface_attributes
            is_collision = level_model_props.sa1_surface_attribute_0 or level_model_props.sa1_surface_attribute_1
            is_visual = level_model_props.sa1_surface_attribute_31

        elif index < self._level.visual_count:
            level_model_props.sa2_visual_surface_attributes = model.surface_attributes
            is_visual = True
            is_collision = False

        else:
            level_model_props.sa2_collision_surface_attributes = model.surface_attributes
            is_visual = False
            is_collision = True

        if is_collision and is_visual:
            self._hybrid_collection.objects.link(obj)
        
        if is_visual:
            self._visual_collection.objects.link(obj)
        
        if is_collision:
            self._collision_collection.objects.link(obj)

        if not is_collision and not is_visual:
            self._neither_collection.objects.link(obj)

        return obj

    def convert_level(self, level: CLevel):
        self._level = level
        self._objects = []

        self._setup_collections()
        self._setup_meshes()

        for i in range(level.models_size):
            model: CLevelModel = level.models[i]
            self._objects.append(self._setup_object(i, model))

        self._cleanup_collections()

        return self._collection, model

    def reset(self):
        self._mesh_converter.reset()