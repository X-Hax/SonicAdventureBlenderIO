import bpy

from . import i_enum
from .i_motion import ShapeMotionProcessor

from ..utility.camera_utils import CameraSetup
from ..utility.event_lut import (
    OVERLAY_UPGRADE_LUT,
    INTEGRATED_UPGRADE_LUT
)

from ..dotnet import SAIO_NET


class EventImporter:

    context: bpy.types.Context
    name: str
    optimize: bool
    auto_normals: bool
    event_data: any
    scene_data: list

    base_scene: bpy.types.Scene
    texture_world: bpy.types.World
    texturename_world: bpy.types.World
    cuts: list[bpy.types.Scene]

    shared_collection: bpy.types.Collection
    camera_collection: bpy.types.Collection
    cut_collections: list[bpy.types.Collection]
    gcshadow_collection: bpy.types.Collection
    particle_collection: bpy.types.Collection
    upgrades_collection: bpy.types.Collection
    reflections_collection: bpy.types.Collection

    camera_setup: CameraSetup
    camera_nlas: tuple[
        bpy.types.NlaTrack,
        bpy.types.NlaTrack,
        bpy.types.NlaTrack]

    particles: list[bpy.types.Object]

    model_name_lut: dict[str, str]

    shape_motion_processor: ShapeMotionProcessor

    def __init__(
            self,
            context: bpy.types.Context,
            name: str,
            optimize: bool,
            auto_normals: bool):

        self.context = context
        self.name = name
        self.optimize = optimize
        self.auto_normals = auto_normals
        self.scene_data = []
        self.cuts = []
        self.cut_collections = []
        self.model_name_lut = {}
        self.particles = []

    def _get_model(self, name):
        if name not in self.model_name_lut:
            return None

        object_name = self.model_name_lut[name]
        if "\n" in object_name:
            object_name = object_name[:object_name.index("\n")]

        return bpy.data.objects[object_name]

    def _get_bone_name(self, name):
        if name not in self.model_name_lut:
            return None

        object_name = self.model_name_lut[name]
        if "\n" in object_name:
            return object_name[object_name.index("\n")+1:]

        return None

    ######################################################################

    def _setup_scenes(self):

        self.texture_world = bpy.data.worlds.new(self.name + "_tex")
        self.texturename_world = bpy.data.worlds.new(self.name + "_texname")

        self.base_scene = bpy.data.scenes.new(self.name)
        self.base_scene.saio_scene.display_specular = False
        self.base_scene.saio_scene.texture_world = self.texture_world
        self.base_scene.saio_scene.texturename_world = self.texturename_world
        self.context.window.scene = self.base_scene

        self.base_scene.saio_scene.scene_type = 'EVR'
        event_props = self.base_scene.saio_scene.event

        framecount = 0
        for i, scene_data in enumerate(self.event_data.EventData.Scenes):
            if i == 0:
                continue

            self.scene_data.append(scene_data)

            cut_scene = bpy.data.scenes.new(f"{self.name}_{i:02}")

            cut_scene.render.resolution_x = 1440
            cut_scene.render.resolution_y = 1080
            cut_scene.saio_scene.scene_type = 'EVC'
            cut_scene.saio_scene.display_specular = False
            cut_scene.saio_scene.texture_world = self.texture_world
            cut_scene.saio_scene.texturename_world = self.texturename_world

            cut_scene.frame_start = framecount
            framecount += scene_data.FrameCount
            cut_scene.frame_end = framecount - 1
            cut_scene.render.fps = 30

            self.cuts.append(cut_scene)
            event_props.new(scene=cut_scene, name=f"Scene {i}")

    def _setup_collections(self):

        def create(append):
            result = bpy.data.collections.new(self.name + append)
            self.base_scene.collection.children.link(result)
            return result

        self.shared_collection = create("_shared")
        self.camera_collection = create("_camera")
        self.gcshadow_collection = create("_shadows")
        self.upgrades_collection = create("_upgrades")
        self.reflections_collection = create("_reflections")

        self.particle_collection = bpy.data.collections.new(
            self.name + "_particles")

        for cut in self.cuts:
            cut_collection = bpy.data.collections.new(cut.name)
            self.cut_collections.append(cut_collection)

            cut.collection.children.link(self.shared_collection)
            cut.collection.children.link(self.camera_collection)
            cut.collection.children.link(self.particle_collection)
            cut.collection.children.link(cut_collection)

    def _setup_camera(self):
        self.camera_setup = CameraSetup.create_setup(
            self.name, self.camera_collection, True)

        self.camera_nlas = (
            self.camera_setup.camera.animation_data.nla_tracks[0],
            self.camera_setup.target.animation_data.nla_tracks[0],
            self.camera_setup.camera_data.animation_data.nla_tracks[0],
        )

        camera = self.camera_setup.camera_data
        camera.clip_start = 1
        camera.clip_end = 100000

        for scene in self.cuts:
            scene.camera = self.camera_setup.camera

    def _load_textures(self):
        from . import i_texture
        if self.event_data.Textures is not None:
            i_texture.process_texture_set(
                self.event_data.Textures,
                self.texture_world.saio_texture_list
            )

        if self.event_data.TexNames is not None:
            i_texture.process_texture_names(
                self.event_data.TexNames,
                self.texturename_world.saio_texturename_list
            )

    ######################################################################

    def _import_models(self):
        from .i_node import NodeProcessor

        processor = NodeProcessor(
            self.context,
            self.base_scene.collection,
            False,
            self.auto_normals,
            False,
            False,
            self.model_name_lut
        )

        for model in self.event_data.Models:

            as_armature = (
                model.Root.ChildCount > 0
                and model.Root not in self.event_data.NotArmaturedModels)
            weighted_name = model.Root.Label

            processor.process(
                model,
                weighted_name,
                self.name,
                as_armature
            )

            if weighted_name in self.model_name_lut:
                output = self._get_model(weighted_name)
            else:
                output = self._get_model(model.Root.Label)

            output.saio_event_entry.entry_type = 'NONE'

        processor.setup_materials()

    def _add_model_to_collection(self, model, collection):

        def add_hierarchy(obj):
            collection.objects.link(obj)
            for child in obj.children:
                add_hierarchy(child)

        def add_hierarchy_clone(obj: bpy.types.Object, num):
            clone = obj.copy()
            clone.name = f"{model.Label}_{num:03}"
            collection.objects.link(clone)

            if clone.data is not None:
                clone.data = obj.data.copy()
                clone.data.name = f"{obj.data.name}_{num:03}"

            for child in obj.children:
                add_hierarchy_clone(child, num)

            return clone

        obj = self._get_model(model.Label)
        if obj.name in collection.objects:
            append = 0
            while True:
                append += 1
                name = f"{model.Label}_{append:03}"
                index = bpy.data.objects.find(name)
                if index == -1:
                    obj = None
                    break
                obj = bpy.data.objects[index]
                if obj.name not in collection.objects:
                    break

            if obj is None:
                obj = add_hierarchy_clone(
                    self._get_model(model.Label), append)
                self.model_name_lut[name] = obj.name
            else:
                add_hierarchy(obj)
        else:
            add_hierarchy(obj)

        return obj

    def _add_entity_to_collection(
            self, model, collection, entry_type, attributes, layer, shadowmodel):
        if model is None:
            return

        obj = self._add_model_to_collection(model, collection)

        evententry_properties = obj.saio_event_entry
        evententry_properties.entry_type = entry_type

        if entry_type != 'SHADOW':
            evententry_properties.shadow_model = shadowmodel
            evententry_properties.layer = layer
            i_enum.from_evententry_attributes(
                evententry_properties, attributes)

    def _add_scene_entities_to_collection(self, entities, collection):
        for entity in entities:
            shadow_object = None
            if entity.ShadowModel is not None:
                shadow_object = self._get_model(entity.ShadowModel.Label)
                if shadow_object.saio_event_entry.entry_type == 'NONE':
                    self._add_entity_to_collection(
                        entity.ShadowModel, self.gcshadow_collection, 'SHADOW',
                        None, None, None)

            self._add_entity_to_collection(
                entity.Model, collection, "CHUNK",
                entity.Attributes, entity.Layer, shadow_object)

            self._add_entity_to_collection(
                entity.GCModel, collection, "GC",
                entity.Attributes, entity.Layer, shadow_object)

    def _setup_attach_upgrade(self, model, target, index, second):
        if model is None:
            return

        obj = self._add_model_to_collection(model, self.upgrades_collection)

        upgrade_properties = getattr(
            self.base_scene.saio_scene.event,
            "au_" + OVERLAY_UPGRADE_LUT[index].lower())

        setattr(upgrade_properties, f"model{(2 if second else 1)}", obj)

        if target is None:
            return

        target_object = self._get_model(target.Label)
        setattr(
            upgrade_properties,
            f"target{(2 if second else 1)}",
            target_object)

        if target_object.type == "ARMATURE":
            setattr(
                upgrade_properties,
                f"target{(2 if second else 1)}_bone",
                self._get_bone_name(target.Label))

    def _setup_override_upgrade(self, model, index, upgrade_type):
        if model is None:
            return

        upgrade_properties = getattr(
            self.base_scene.saio_scene.event,
            "ou_" + INTEGRATED_UPGRADE_LUT[index].lower())

        fieldname = "override2"
        if upgrade_type == 1:
            fieldname = "override1"
        elif upgrade_type == 2:
            fieldname = "base"

        target_object = self._get_model(model.Label)
        setattr(
            upgrade_properties,
            fieldname,
            target_object)

        if target_object.type == "ARMATURE":
            setattr(
                upgrade_properties,
                f"{fieldname}_bone",
                self._get_bone_name(model.Label))

    def _categorize_models(self):
        import math

        # upgrades
        for i, upgrade in enumerate(self.event_data.EventData.OverlayUpgrades):
            self._setup_attach_upgrade(
                upgrade.Model1, upgrade.Target1, i, False)
            self._setup_attach_upgrade(
                upgrade.Model2, upgrade.Target2, i, True)

        for i, model in enumerate(self.event_data.EventData.IntegratedUpgrades):
            self._setup_override_upgrade(
                model,
                math.floor(i / 3),
                i % 3)

        # base entities
        self._add_scene_entities_to_collection(
            self.event_data.EventData.Scenes[0].Entries,
            self.shared_collection)

        # per-scene entities
        for col, scene_data in zip(self.cut_collections, self.scene_data):
            self._add_scene_entities_to_collection(scene_data.Entries, col)

        # removing models from base scene collection
        for obj in list(self.base_scene.collection.objects):
            if len(obj.users_collection) > 1:
                self.base_scene.collection.objects.unlink(obj)

    ######################################################################

    def _setup_particles(self):

        particle_count = 0
        for scene in self.event_data.EventData.Scenes:
            particle_count = max(particle_count, len(scene.ParticleMotions))

        for i in range(particle_count):

            obj = bpy.data.objects.new(f"{self.name}_particle_{i:03}", None)
            obj.saio_event_entry.entry_type = 'PARTICLE'

            self.particle_collection.objects.link(obj)
            self.particles.append(obj)

    def _setup_other_models(self):
        from mathutils import Vector

        event_properties = self.base_scene.saio_scene.event

        if self.event_data.EventData.TailsTails is not None:
            tt = self.event_data.EventData.TailsTails
            tt_object = self._get_model(tt.Label)
            event_properties.tails_tails = tt_object
            if tt_object.type == "ARMATURE":
                event_properties.tails_tails_bone = self._get_bone_name(
                    tt.Label)

        reflections = self.event_data.EventData.Reflections
        for i, reflection in enumerate(reflections.Reflections):

            verts = [
                Vector((reflection.Vertex1.X, -reflection.Vertex1.Z, reflection.Vertex1.Y)),
                Vector((reflection.Vertex2.X, -reflection.Vertex2.Z, reflection.Vertex2.Y)),
                Vector((reflection.Vertex3.X, -reflection.Vertex3.Z, reflection.Vertex3.Y)),
                Vector((reflection.Vertex4.X, -reflection.Vertex4.Z, reflection.Vertex4.Y)),
            ]
            center = Vector()
            for vert in verts:
                center += vert

            center *= 0.25
            verts = [v - center for v in verts]
            tris = [(0, 1, 2), (1, 3, 2)]

            mesh = bpy.data.meshes.new(f"{self.name}_refl_{i:03}")
            mesh.from_pydata(verts, [], tris)

            obj = bpy.data.objects.new(mesh.name, mesh)
            obj.location = center
            obj.saio_event_entry.entry_type = "REFLECTION"
            obj.color = (1, 1, 1, reflection.Transparency)

            self.reflections_collection.objects.link(obj)

    ######################################################################

    def _setup_camera_animations(self, animations, frame: int):
        from .i_motion import CameraMotionProcessor

        for camera_animation in animations:
            if camera_animation.Animation is None:
                continue

            camera_actions = CameraMotionProcessor.process_motion(
                camera_animation.Animation,
                self.camera_setup)

            def setup_action(index, action):
                strip = self.camera_nlas[index].strips.new(
                    action.name, frame, action)
                strip.extrapolation = 'NOTHING'

            setup_action(0, camera_actions.position)
            setup_action(1, camera_actions.target)
            setup_action(2, camera_actions.fov)

            break

    def _setup_node_animation(
            self,
            obj: bpy.types.Object,
            motion,
            frame: int):
        from .i_motion import NodeMotionProcessor

        action = NodeMotionProcessor.process_motion(
            motion,
            obj,
            "ANIM",
            0.01)

        anim_data = obj.animation_data
        if anim_data is None:
            anim_data = obj.animation_data_create()

            # if bones have a default scale, we need to
            # add those in a lower nla track
            if obj.type == "ARMATURE" \
                and any([not b.bone.saio_node.ignore_scale
                        for b in obj.pose.bones]):

                scale_action = bpy.data.actions.new(
                    obj.name + "_scales")
                for b in obj.pose.bones:
                    if b.bone.saio_node.ignore_scale:
                        continue

                    scales = [
                        scale_action.fcurves.new(
                            f"pose.bones[\"{b.name}\"].scale",
                            index=i,
                            action_group=b.name).keyframe_points
                        for i in range(3)
                    ]

                    for i in range(3):
                        scales[i].insert(0, b.scale[i])

                scale_nla = anim_data.nla_tracks.new()
                scale_nla.name = "Default Scale"
                scale_strip = scale_nla.strips.new(
                    action.name, 0, scale_action)
                scale_strip.extrapolation = 'HOLD_FORWARD'

            nla = anim_data.nla_tracks.new()
        else:
            nla = anim_data.nla_tracks[-1]

        strip = nla.strips.new(action.name, frame, action)
        strip.extrapolation = 'HOLD_FORWARD'

    def _setup_entitity_shape_animation(
            self,
            obj: bpy.types.Object,
            motion,
            frame: int,
            frame_num: int):

        actions = self.shape_motion_processor.process(
            motion, obj, frame_num)

        for obj, action in actions.items():
            shape_keys: bpy.types.Key = obj.data.shape_keys
            if shape_keys.animation_data is None:
                shape_keys.animation_data_create()
                nla = shape_keys.animation_data.nla_tracks.new()
            else:
                nla = shape_keys.animation_data.nla_tracks[0]

            strip = nla.strips.new(action.name, frame, action)
            strip.extrapolation = 'NOTHING'

    def _setup_entity_animation(
            self,
            entity,
            scene_model_names_used: dict,
            start_frame: int,
            frame_num: int):
        model = entity.Model
        if model is None:
            model = entity.GCModel

        name = model.Label
        if name not in scene_model_names_used:
            scene_model_names_used[name] = 1
        else:
            num = 1
            name = f"{model.Label}_{num:03}"
            while name in scene_model_names_used:
                num += 1
                name = f"{model.Label}_{num:03}"

        obj = self._get_model(name)

        if entity.Animation is not None:
            self._setup_node_animation(
                obj, entity.Animation, start_frame)

        if entity.ShapeAnimation is not None:
            self._setup_entitity_shape_animation(
                obj,
                entity.ShapeAnimation,
                start_frame,
                frame_num)

    def _setup_animations(self):

        self.shape_motion_processor = ShapeMotionProcessor(self.optimize)

        for cut_scene, scene_data in zip(self.cuts, self.scene_data):
            frame_num = cut_scene.frame_end - cut_scene.frame_start + 1

            self._setup_camera_animations(
                scene_data.CameraAnimations, cut_scene.frame_start)

            scene_model_names_used = {}

            for i, anim in enumerate(scene_data.ParticleMotions):
                if anim is None:
                    continue
                self._setup_node_animation(
                    self.particles[i],
                    anim,
                    cut_scene.frame_start)

            for entity in scene_data.Entries:
                self._setup_entity_animation(
                    entity,
                    scene_model_names_used,
                    cut_scene.frame_start,
                    frame_num)

    ######################################################################

    def _setup_other(self):
        self.base_scene.saio_scene.event.drop_shadow_control \
            = self.event_data.EventData.EnableDropShadows

        if self.event_data.EventData.SurfaceAnimations is not None:
            animdata = self.event_data.EventData.SurfaceAnimations
            event_uv_anim_list = self.base_scene.saio_scene.event.uv_animations

            for ts in animdata.TextureSequences:
                element = event_uv_anim_list.new()
                element.texture_index = ts.TextureID
                element.texture_count = ts.TextureCount

            for block in animdata.AnimationBlocks:
                model = self._get_model(block.Model.Label)
                if model.type == "ARMATURE":
                    print(f"Warning: model {block.Model.Label} has uv"
                          " animations, but the addon does not support"
                          " uv animations on armature models!")
                    continue

                node_uv_anim_list = model.saio_eventnode_uvanims

                for anim in block.Animations:
                    if anim is None:
                        continue

                    element = node_uv_anim_list.new()

                    element.material_index = SAIO_NET.CUTSCENE.GetMaterialIndex(
                        block.Model, anim.TextureChunk)

    def process(self, event_data):
        self.event_data = event_data

        self._setup_scenes()
        self._setup_collections()
        self._setup_camera()

        self._load_textures()
        self._import_models()
        self._categorize_models()

        self._setup_particles()
        self._setup_other_models()

        self._setup_animations()

        self._setup_other()
