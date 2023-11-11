import bpy
from bpy.types import Object as BObject

from .o_shapemotion import (
    check_is_shape_motion_viable,
    ShapeActionCollection,
    ShapeMotionEvaluator
)
from .o_model import ModelEvaluator, ModelData
from ..utility.event_lut import *
from ..utility.anim_parameters import AnimParameters
from ..utility import camera_utils
from ..exceptions import UserException


def get_base_scene(context: bpy.types.Context):
    scene = context.scene
    if scene.saio_scene.scene_type == 'EVR':
        return scene

    result = None
    for bscene in bpy.data.scenes:
        if (bscene.saio_scene.scene_type != 'EVR'):
            continue

        found = False
        for event_scene in bscene.saio_scene.event:
            if event_scene.scene == scene:
                found = True
                break

        if not found:
            continue

        if result is not None:
            raise UserException(
                "Multiple base scenes containing export scene found!")

        result = bscene

    if result is None:
        raise UserException("No base scene found!")

    return result


class CutInfo:

    context: bpy.types.Context
    scene: bpy.types.Scene
    index: int
    particles: list[BObject]
    models: dict[BObject, ModelData]
    anim_parameters: AnimParameters
    shape_motion_evaluators: dict[BObject, ShapeMotionEvaluator]

    entries: list[BObject]
    duration: int

    temp_actions: list[bpy.types.Action]
    output_actions: dict[BObject, bpy.types.Action]
    output_shape_actions: dict[BObject, ShapeActionCollection]
    action_setup_dict: dict[bpy.types.FCurve, any]

    camera_setup: camera_utils.CameraSetup
    camera_actions: camera_utils.CameraActionSet

    motions: dict[BObject, any]
    shape_motions: dict[BObject, any]
    camera_motion: any

    def __init__(
            self,
            context: bpy.types.Context,
            scene: bpy.types.Scene,
            index: int,
            models: dict[BObject, ModelData],
            anim_parameters: AnimParameters,
            shape_motion_evaluators: dict):

        self.context = context
        self.scene = scene
        self.index = index
        self.entries = []
        self.particles = []
        self.anim_parameters = anim_parameters
        self.models = models
        self.shape_motion_evaluators = shape_motion_evaluators

        self.duration = scene.frame_end - scene.frame_start

        self.temp_actions = []
        self.output_actions = {}
        self.output_shape_actions = {}
        self.action_setup_dict = {}

        self.camera_setup = camera_utils.CameraSetup.get_setup(
            self.scene.camera)

        if self.camera_setup is None:
            raise UserException(
                f"Camera setup in scene {self.scene.name} is invalid!")

        self.camera_actions = None

        self.motions = {}
        self.shape_motions = {}
        self.camera_motion = None

    @property
    def framecount(self):
        # a scene from 0 to 1 has 2 frames, but 1 - 0 is 1, so we gotta add 1
        return self.duration + 1

    def _setup_motion_scene(self):

        self.context.window.scene = self.scene
        self.scene.frame_current = self.scene.frame_start

    ######################################################################

    def _is_animated(self, animdata):
        if animdata is None:
            return False

        stripcount = sum([
            len(track.strips)
            for track
            in animdata.nla_tracks]
        )

        return stripcount > 0

    def _get_matching_action(self, anim: bpy.types.AnimData):

        tracks = [track for track in anim.nla_tracks if len(track.strips) > 0]
        if len(tracks) != 1:
            return None
        track = tracks[0]

        matching_strip = None
        for strip in track.strips:
            if (strip.frame_start == self.scene.frame_start
                    and strip.frame_end == self.scene.frame_end):
                matching_strip = strip
                break

        if matching_strip is None or matching_strip.type != 'CLIP':
            return None

        frame_range = matching_strip.action.frame_range
        frame_length = frame_range[1] - frame_range[0]
        if (frame_length == self.duration
                and len(matching_strip.modifiers) == 0
                and matching_strip.scale == 1):
            return matching_strip.action

        return None

    def _setup_action(self, animdata, name, on_create, ensure_action=False):
        if not self._is_animated(animdata) and not ensure_action:
            return None

        action = self._get_matching_action(animdata)

        if action is None:
            action = bpy.data.actions.new(
                f"SAIO_{self.scene.name}_{name}")
            self.temp_actions.append(action)

            on_create(action)

        return action

    ######################################################################

    def _setup_temp_armature_action(
            self,
            action: bpy.types.Action,
            object: BObject):

        for bone in object.pose.bones:

            def create_curve(field, len):
                for i in range(len):
                    curve = action.fcurves.new(
                        f"pose.bones[\"{bone.name}\"].{field}",
                        index=i,
                        action_group=bone.name)
                    self.action_setup_dict[curve] = (bone, field, i)

            create_curve("location", 3)
            create_curve("scale", 3)

            if bone.rotation_mode == 'QUATERNION':
                create_curve("rotation_quaternion", 4)
            else:
                create_curve("rotation_euler", 3)

    def _setup_temp_object_action(
            self,
            action: bpy.types.Action,
            object: BObject,
            only_location: bool = False):

        def create_curve(field, len):
            for i in range(len):
                curve = action.fcurves.new(
                    field,
                    index=i,
                    action_group="transforms")
                self.action_setup_dict[curve] = (object, field, i)

        create_curve("location", 3)

        if only_location:
            return

        create_curve("scale", 3)

        if object.rotation_mode == 'QUATERNION':
            create_curve("rotation_quaternion", 4)
        else:
            create_curve("rotation_euler", 3)

    def _setup_temp_target_action(self, action: bpy.types.Action, object):

        def create_curve(field, index):
            curve = action.fcurves.new(
                field,
                index=index,
                action_group="transforms")
            self.action_setup_dict[curve] = (object, field, index)

        for i in range(3):
            create_curve("location", i)
        create_curve("rotation_euler", 2)

    def _setup_temp_fov_action(self, action: bpy.types.Action, object):
        action.id_root = 'CAMERA'
        curve = action.fcurves.new(
            "lens",
            action_group="camera")
        self.action_setup_dict[curve] = (object, "lens", None)

    ######################################################################

    def _get_shape_action(self, object: BObject):
        if object.type != 'MESH':
            return None

        from ..utility.general import get_armature_modifier
        if get_armature_modifier(object) is not None:
            return None

        keys: bpy.types.Key = object.data.shape_keys
        if keys is None or keys.animation_data is None:
            return None

        target_track = None
        for track in keys.animation_data.nla_tracks:
            if len(track.strips) == 0:
                continue

            if target_track is not None:
                raise UserException(
                    f"Object {object.name} has multiple NLA tracks on its"
                    " shape data!")

            target_track = track

        if target_track is None:
            return None

        target_strip = None
        for strip in target_track.strips:
            if (strip.frame_start == self.scene.frame_start
                    and strip.frame_end == self.scene.frame_end):
                target_strip = strip
                continue

            if not (strip.frame_start > self.scene.frame_end
                    or strip.frame_end < self.scene.frame_start):
                raise UserException(
                    "All shape actions on an nla track have to fit"
                    " exactly onto the scene they are played in! Object"
                    f" {object.name} does not comply!")

        if target_strip is None or target_strip.type != 'CLIP':
            return None

        frame_range = target_strip.action.frame_range
        frame_length = frame_range[1] - frame_range[0]
        if (frame_length != self.duration
                or len(target_strip.modifiers) != 0
                or target_strip.scale != 1):

            raise UserException(
                f"Shape action {target_strip.action.name}"
                f" on object {object.name} does not match with its strip"
                " or is not \"vanilla\"!")

        return target_strip.action

    def _collect_shape_actions(self, entry: BObject):
        shape_actions = ShapeActionCollection()

        if entry.type == 'ARMATURE':
            for child in entry.children:
                if child.parent_type != 'BONE':
                    continue
                action = self._get_shape_action(child)
                if action is not None:
                    shape_actions.actions[child] = action

            if len(shape_actions.actions) > 0:
                check_is_shape_motion_viable(entry)

        else:
            action = self._get_shape_action(entry)
            if action is not None:
                shape_actions.actions[entry] = action

        if len(shape_actions.actions) > 0:
            shape_actions.name = f"Event{self.index}_{entry.name}_Shape"
            self.output_shape_actions[entry] = shape_actions

    def _prepare_entry_actions(self):

        for entry in self.entries:
            if entry.type != 'ARMATURE' and len(entry.children) > 0:
                continue

            # Node animation

            def create(x):
                if entry.type == 'ARMATURE':
                    self._setup_temp_armature_action(x, entry)
                else:
                    self._setup_temp_object_action(x, entry)

            action = self._setup_action(
                entry.animation_data,
                f"Scene{self.index:02}_{entry.name}",
                create)

            if action is not None:
                self.output_actions[entry] = action

            self._collect_shape_actions(entry)

    def _prepare_particle_actions(self):

        for particle in self.particles:

            action = self._setup_action(
                particle.animation_data,
                particle.name,
                lambda x: self._setup_temp_object_action(x, particle, True))

            if action is not None:
                self.output_actions[particle] = action

    def _prepare_camera_actions(self):

        camera_action = self._setup_action(
            self.camera_setup.camera.animation_data,
            "camera",
            lambda x: self._setup_temp_object_action(
                x, self.camera_setup.camera, True),
            True)

        target_action = self._setup_action(
            self.camera_setup.target.animation_data,
            "target",
            lambda x: self._setup_temp_target_action(
                x, self.camera_setup.target),
            True)

        fov_action = self._setup_action(
            self.camera_setup.camera_data.animation_data,
            "fov",
            lambda x: self._setup_temp_fov_action(
                x, self.camera_setup.camera_data),
            True)

        self.camera_actions = camera_utils.CameraActionSet(
            camera_action,
            target_action,
            fov_action)

    ######################################################################

    def _eval_action_keyframes(self):
        if len(self.action_setup_dict) == 0:
            return

        for i in range(self.framecount):
            self.context.view_layer.update()

            for curve, params in self.action_setup_dict.items():
                value = getattr(params[0], params[1])
                if params[2] is not None:
                    value = value[params[2]]
                curve.keyframe_points.insert(i, value).interpolation = 'LINEAR'

            self.scene.frame_current += 1

    def _convert_actions(self):
        from .o_motion import convert_to_node_motion, convert_to_camera_motion

        self.camera_motion = convert_to_camera_motion(
            self.camera_setup,
            self.camera_actions,
            f"Scene{self.index:02}_Camera",
            self.anim_parameters
        )

        for object, action in self.output_actions.items():
            self.motions[object] = convert_to_node_motion(
                object,
                False,
                action.fcurves,
                action.frame_range,
                action.name,
                self.anim_parameters
            )

        if len(self.output_shape_actions) > 0:

            for object, actions in self.output_shape_actions.items():
                if object not in self.shape_motion_evaluators:
                    evaluator = ShapeMotionEvaluator(
                        self.models[object],
                        self.context,
                        'NONE')
                    self.shape_motion_evaluators[object] = evaluator
                else:
                    evaluator = self.shape_motion_evaluators[object]

                self.shape_motions[object] = evaluator.evaluate(actions)

    def _cleanup(self):
        for action in self.temp_actions:
            bpy.data.actions.remove(action)

    def evaluate_motions(self):
        self._setup_motion_scene()

        self._prepare_entry_actions()
        self._prepare_camera_actions()
        self._prepare_particle_actions()

        self._eval_action_keyframes()

        self._convert_actions()
        self._cleanup()


class EventExporter:

    context: bpy.types.Context
    optimize: bool
    anim_parameters: AnimParameters

    base_scene: bpy.types.Scene
    shared_entries: list[BObject]

    shadows: list[BObject]
    upgrades: list[BObject]
    reflections: list[BObject]
    blare: list[BObject]
    uv_animated_objects: list[BObject]
    '''(entry model, target object)'''
    total_framecount: int

    cut_scenes: list[CutInfo]
    entry_source_scene: dict[BObject, bpy.types.Scene]

    shape_motion_evaluators: dict[BObject, ShapeMotionEvaluator]
    models: dict[BObject, ModelData]
    nodes: dict[BObject | bpy.types.Bone, any]

    sa2_evaluator: ModelEvaluator
    sa2b_evaluator: ModelEvaluator

    event_data: any

    def __init__(
            self,
            context: bpy.types.Context,
            optimize: bool,
            auto_node_attributes: bool,
            anim_parameters: AnimParameters):

        self.context = context
        self.optimize = optimize
        self.anim_parameters = anim_parameters

        self.base_scene = None
        self.shared_entries = []

        self.shadows = []
        self.upgrades = []
        self.reflections = []
        self.blare = []
        self.uv_animated_objects = []
        self.total_framecount = 0

        self.cut_scenes = []
        self.entry_source_scene = {}

        self.shape_motion_evaluators = {}
        self.models = {}
        self.nodes = {}

        def get_evaluator(chunk: bool):
            return ModelEvaluator(
                self.context,
                'SA2' if chunk else 'SA2B',
                False,
                self.optimize,
                not chunk,
                False,
                True,
                False,
                auto_node_attributes,
                False
            )

        self.sa2_evaluator = get_evaluator(True)
        self.sa2b_evaluator = get_evaluator(False)

    def _collect_scenes(self):

        self.base_scene = get_base_scene(self.context)

        if self.base_scene is None:
            raise UserException("No base scene containg export scene found!")

        for i, scene in enumerate(self.base_scene.saio_scene.event):
            if scene is None:
                continue

            cutinfo = CutInfo(
                self.context,
                scene.scene,
                i,
                self.models,
                self.anim_parameters,
                self.shape_motion_evaluators)

            self.cut_scenes.append(cutinfo)
            self.total_framecount += cutinfo.framecount

    def _collect_objects(self):

        for object in self.base_scene.objects:
            if object.parent is not None:
                continue

            type = object.saio_event_entry.entry_type

            if type == "NONE":
                continue
            elif type == "SHADOW":
                self.shadows.append(object)
            elif type == "REFLECTION":
                self.reflections.append(object)
            elif type != "PARTICLE":
                self.shared_entries.append(object)

            self.entry_source_scene[object] = self.base_scene

        self.shared_entries.sort(key=lambda x: x.name)

        event_properties = self.base_scene.saio_scene.event
        for name in ATTACH_UPGRADE_LUT.values():
            if not isinstance(name, str):
                continue

            upgrade_properties = getattr(
                event_properties,
                "au_" + name.lower())

            model1 = upgrade_properties.model1
            if model1 is not None:
                if model1.parent is not None:
                    raise UserException(
                        f"Model1 of attach upgrade {name}"
                        " is not a root object!")
                self.upgrades.append(model1)
                self.entry_source_scene[model1] = self.base_scene

            model2 = upgrade_properties.model2
            if model2 is not None:
                if model2.parent is not None:
                    raise UserException(
                        f"Model2 of attach upgrade {name}"
                        " is not a root object!")
                self.upgrades.append(model2)
                self.entry_source_scene[model2] = self.base_scene

        for cutinfo in self.cut_scenes:

            for object in cutinfo.scene.objects:
                if (object.parent is not None
                        or object.name in self.base_scene.objects):
                    continue

                type = object.saio_event_entry.entry_type

                if type == "PARTICLE":
                    cutinfo.particles.append(object)
                elif type in ["CHUNK", "GC"]:
                    cutinfo.entries.append(object)

                    if object.saio_event_entry.blare:
                        self.blare.append(object)

                if object not in self.entry_source_scene:
                    self.entry_source_scene[object] = cutinfo.scene

        if len(self.blare) > 64:
            raise UserException("Can't have more than 64 blare models!")

    ######################################################################

    def _get_children(
            self,
            object: BObject,
            output: list[BObject]):

        output.append(object)
        for child in object.children:
            self._get_children(child, output)

    def _convert_model(self, object: bpy.types.Object):
        objects = []
        self._get_children(object, objects)

        event_props = object.saio_event_entry
        evaluator = (self.sa2b_evaluator
                     if event_props.entry_type == 'GC'
                     else self.sa2_evaluator)

        # to ensure the correct depsgraph. otherwise triangulating
        # may not always work (or other related functionalities)
        self.context.window.scene = self.entry_source_scene[object]

        model_data = evaluator.evaluate(objects)

        self.models[object] = model_data

        nodes = model_data.outdata.GetNodes()
        mapping = model_data.node_data.node_mapping

        for node_source, node_index in mapping.items():
            self.nodes[node_source] = nodes[node_index]

        uv_meshes = []
        for object in objects:
            uv_anims = object.saio_eventnode_uvanims
            if len(uv_anims) > 0:
                uv_meshes.append(object)

        if len(uv_meshes) > 0:
            if event_props.entry_type == 'GC':
                raise UserException(
                    f"Error on {uv_meshes[0].name}:"
                    " GC Models cannot have uv animations")
            elif event_props.entry_type == 'SHADOW':
                raise UserException(
                    f"Error on {uv_meshes[0].name}:"
                    " Shadow models cannot have uv animations")
            elif object.type == 'ARMATURE':
                raise UserException(
                    f"Error on {uv_meshes[0].name}:"
                    " Armature models do not support uv animations"
                    " (in blender)")

            self.uv_animated_objects.extend(uv_meshes)

    def _convert_models(self):
        base_entries = []
        base_entries.extend(self.shared_entries)
        base_entries.extend(self.shadows)
        base_entries.extend(self.upgrades)
        base_entries = set(base_entries)

        for entry in base_entries:
            self._convert_model(entry)

        converted = {}

        for cut in self.cut_scenes:
            self.context.window.scene = cut.scene
            for entry in cut.entries:
                if entry not in converted:
                    converted[entry] = None
                    self._convert_model(entry)

    def _evaluate_motions(self):

        for cut in self.cut_scenes:
            cut.evaluate_motions()

    ######################################################################

    def _setup_texture_dimensions(self):
        from System import ValueTuple, Int16

        if self.base_scene.saio_scene.texture_world is None:
            raise UserException("Base scene has no texture list")

        textures = self.base_scene.saio_scene.texture_world.saio_texture_list

        if len(textures) == 0:
            raise UserException(
                "Base scene has no textures in texture list")

        texture_sizes = []
        type = ValueTuple[Int16, Int16]

        for texture in textures:
            width = texture.override_width
            height = texture.override_height

            if texture.image is not None:
                if width == 0:
                    width = int(texture.image.size[0])
                if height == 0:
                    height = int(texture.image.size[1])
            else:
                if width == 0:
                    width = 1
                if height == 0:
                    height = 1

            texture_sizes.append(type(width, height))

        self.event_data.TextureDimensions = texture_sizes

    def _setup_texture_names(self):

        from . import o_texture

        world = self.base_scene.saio_scene.texturename_world
        if world is not None and len(world.saio_texturename_list) > 0:
            self.event_data.TextureNameList = \
                o_texture.create_texnames_from_names(
                    world.saio_texturename_list, "event")
            return

        world = self.base_scene.saio_scene.texture_world
        if world is not None and len(world.saio_texture_list) > 0:
            self.event_data.TextureNameList = \
                o_texture.create_texnames_from_textures(
                    world.saio_texture_list, "event")
            return

        raise UserException("Base scene has no textures in texture list")

    def _setup_attach_upgrades(self):

        event_properties = self.base_scene.saio_scene.event
        for index, name in ATTACH_UPGRADE_LUT.items():
            if not isinstance(index, int):
                continue

            upgrade_properties = getattr(
                event_properties,
                "au_" + name.lower())

            target_objects = [None, None]
            targets = [None, None]
            models = [None, None]
            found = False
            armature = False

            for sub_index in range(2):
                model = getattr(upgrade_properties, f"model{sub_index + 1}")
                if model is None:
                    continue

                models[sub_index] = self.nodes[model]
                found = True

                target: BObject = getattr(
                    upgrade_properties,
                    f"target{sub_index + 1}")
                target_objects[sub_index] = target

                if target.type == 'ARMATURE':
                    armature = True
                    bone_name = getattr(
                        upgrade_properties,
                        f"target{sub_index + 1}_bone")

                    if bone_name == "":
                        raise UserException(
                            "Bone name of attach upgrade"
                            f" {name}-target{sub_index + 1} is empty!")

                    bone = target.pose.bones[bone_name]
                    targets[sub_index] = self.nodes[bone]
                else:
                    targets[sub_index] = self.nodes[target]

            if found:
                root1 = target_objects[0]
                root2 = target_objects[1]
                if not armature:
                    if root1 is not None:
                        while root1.parent is not None:
                            root1 = root1.parent
                    if root2 is not None:
                        while root2.parent is not None:
                            root2 = root2.parent

                if root1 is not None and root2 is not None and root1 != root2:
                    raise UserException(
                        f"Attach upgrade {name} has targets from different"
                        " entries!")

                root = root1
                if root is None:
                    root = root2
                root_node = self.models[root].outdata

                upgrade_structure = self.event_data.Upgrades[index]

                upgrade_structure.Root = root_node
                upgrade_structure.Target1 = targets[0]
                upgrade_structure.Model1 = models[0]
                upgrade_structure.Target2 = targets[1]
                upgrade_structure.Model2 = models[1]

                self.event_data.Upgrades[index] = upgrade_structure

    def _setup_override_upgrades(self):

        event_properties = self.base_scene.saio_scene.event

        for index, name in UPGRADE_LUT.items():
            if not isinstance(index, int):
                continue

            upgrade_properties = getattr(
                event_properties,
                "ou_" + name.lower())

            for sub_index in range(3):

                fieldname = "override2"
                if sub_index == 1:
                    fieldname = "override1"
                elif sub_index == 2:
                    fieldname = "base"

                target_object: BObject = getattr(
                    upgrade_properties,
                    fieldname)

                if target_object is None:
                    continue

                if target_object.type == 'ARMATURE':
                    bone_name = getattr(
                        upgrade_properties,
                        f"{fieldname}_bone")

                    if bone_name == "":
                        raise UserException(
                            "Bone name of override upgrade"
                            f" {name}-{fieldname} is empty!")

                    bone = target_object.pose.bones[bone_name]
                    node = self.nodes[bone]
                else:
                    node = self.nodes[target_object]

                # real_index = index * 3 + sub_index
                self.event_data.OverrideUpgrades[index, sub_index] = node

    def _setup_blare_models(self):

        for index, blare in enumerate(self.blare):
            self.event_data.BlareModels[index] = self.models[blare].outdata

    def _setup_reflection_models(self):

        if len(self.reflections) == 0:
            return

        from SA3D.Event.SA2.Model import ReflectionData, Reflection
        from System.Numerics import Vector3

        reflections = ReflectionData()

        for entry in self.reflections:

            if entry.type != "MESH":
                raise UserException(
                    f"Object {entry.name} is a reflection and not a mesh!")

            mesh: bpy.types.Mesh = entry.data
            if len(mesh.vertices) != 4:
                raise UserException(
                    f"Object {entry.name} has more/less than 4 vertices!")

            reflection = Reflection()

            matrix = entry.matrix_world

            for index, vertex in enumerate(mesh.vertices):
                position = matrix @ vertex.co
                reflection.Quad[index] = Vector3(
                    position.x,
                    position.z,
                    -position.y,
                )

            reflections.Reflections.Add(reflection)

        self.event_data.ReflectionControl = reflections

    def _setup_tails_tails(self):

        event_properties = self.base_scene.saio_scene.event

        if event_properties.tails_tails is None:
            return

        tt_target = event_properties.tails_tails
        if tt_target.type == 'ARMATURE':
            bone = event_properties.tails_tails_bone
            tt_target = tt_target.pose.bones[bone]

        self.event_data.TailsTails = self.nodes[tt_target]

    def _setup_uv_animations(self):
        from SA3D.Modeling.Blender import Cutscene
        from SA3D.Event.SA2.Animation import (
            UVAnimationData,
            UVAnimTextureSequence,
            UVAnimationBlock,
            UVAnimation
        )

        uvanim_data = UVAnimationData()

        # texture sequences
        for uv_anim in self.base_scene.saio_scene.event.uv_animations:
            texture_sequence = UVAnimTextureSequence(
                uv_anim.texture_index,
                uv_anim.texture_count)

            uvanim_data.TextureSequences.Add(texture_sequence)

        for uv_animated_object in self.uv_animated_objects:
            node = self.nodes[uv_animated_object]
            block = UVAnimationBlock(node)
            uvanim_data.AnimationBlocks.Add(block)

            for anim in uv_animated_object.saio_eventnode_uvanims:

                texture_chunk = Cutscene.GetTextureChunkFromMaterialIndex(
                    node, anim.material_index)
                texture_index = texture_chunk.TextureID

                block.Animations.Add(UVAnimation(
                    texture_index, texture_chunk, None))

        if (uvanim_data.TextureSequences.Count > 0
                or uvanim_data.AnimationBlocks.Count > 0):
            self.event_data.UVAnimationData = uvanim_data

    ######################################################################

    def _setup_event_entry(self, object: BObject):
        from SA3D.Event.SA2.Model import EventEntry
        from System.Numerics import Vector3
        from . import o_enum

        entry = EventEntry()

        properties = object.saio_event_entry
        if properties.entry_type == 'GC':
            entry.GCModel = self.models[object].outdata
        else:
            entry.Model = self.models[object].outdata

        if properties.shadow_model is not None:
            if properties.shadow_model not in self.shadows:
                raise UserException(
                    f"Shadow model \"{properties.shadow_model.name}\" for"
                    f" entry \"{object.name}\" is not part of the base"
                    " scene and/or not marked to be a shadow model.")
            entry.ShadowModel = self.models[properties.shadow_model].outdata

        entry.Position = Vector3(
            object.location.x,
            object.location.z,
            -object.location.y,
        )
        entry.Layer = properties.layer

        entry.Attributes = o_enum.to_evententry_attributes(properties)

        return entry

    def _setup_base_scene(self):
        from SA3D.Event.SA2.Model import Scene

        result = Scene(self.total_framecount)
        for object in self.shared_entries:
            entry = self._setup_event_entry(object)
            result.Entries.Add(entry)

        return result

    def _setup_animated_scene(self, cutinfo: CutInfo):
        from SA3D.Event.SA2.Model import Scene, BigTheCat
        from SA3D.Event.SA2.Animation import EventMotion
        from SA3D.Modeling.ObjectData.Animation import AnimationAttributes

        posrot = AnimationAttributes.Position.op_BitwiseOr(
            AnimationAttributes.Rotation)

        result = Scene(cutinfo.framecount)
        result.Big = BigTheCat(None, 0)

        result.CameraAnimations.Add(
            EventMotion.CreateFromMotion(cutinfo.camera_motion))

        for object in cutinfo.entries:
            entry = self._setup_event_entry(object)

            if object in cutinfo.motions:
                entry.Animation = cutinfo.motions[object]
                entry.Animation.EnsureNodeKeyframes(
                    entry.DisplayModel, posrot, True)

            if object in cutinfo.shape_motions:
                entry.ShapeAnimation = cutinfo.shape_motions[object]

            entry.AutoAnimFlags()
            result.Entries.Add(entry)

        for object in cutinfo.particles:
            motion = None
            if object in cutinfo.motions:
                motion = cutinfo.motions[object]
            result.ParticleMotions.Add(motion)

        return result

    def _setup_eventdata(self):
        from SA3D.Event.SA2 import EventType
        from SA3D.Event.SA2.Model import ModelData

        self.event_data = ModelData(EventType.battle)
        self.event_data.DropShadowControl = \
            self.base_scene.saio_scene.event.drop_shadow_control

        self._setup_texture_dimensions()
        self._setup_texture_names()
        self._setup_attach_upgrades()
        self._setup_override_upgrades()
        self._setup_blare_models()
        self._setup_reflection_models()
        self._setup_tails_tails()
        self._setup_uv_animations()

        self.event_data.Scenes.Add(self._setup_base_scene())
        for cutinfo in self.cut_scenes:
            self.event_data.Scenes.Add(self._setup_animated_scene(cutinfo))

    ######################################################################

    def process(self):
        start_scene = self.context.window.scene
        start_frame = start_scene.frame_current

        self._collect_scenes()
        self._collect_objects()
        self._convert_models()
        self._evaluate_motions()

        self._setup_eventdata()

        self.context.window.scene = start_scene
        start_scene.frame_current = start_frame

    def export(self, filepath: str, export_textures: bool):

        from SA3D.Event.SA2 import Event

        event = Event(self.event_data, None, self.event_data.TextureNameList)
        event.WriteToFiles(filepath)

        if export_textures:
            from . import o_texture
            o_texture.save_texture_archive(
                o_texture.create_texture_set(
                    self.base_scene.saio_scene.texture_world.saio_texture_list
                ), filepath[:-4] + "texture.prs",
                "GVM",
                True
            )
