import bpy
from bpy.types import Object as BObject

from . import o_enum
from .o_event_cutinfo import CutInfo
from .o_shapemotion import ShapeMotionEvaluator
from .o_model import ModelEvaluator, ModelData

from ..utility.event_lut import OVERLAY_UPGRADE_LUT, INTEGRATED_UPGRADE_LUT
from ..utility.anim_parameters import AnimParameters
from ..exceptions import UserException

from ..dotnet import System, SAIO_NET, SA3D_Modeling, SA3D_SA2Event


def get_base_scene(context: bpy.types.Context):
    scene = context.scene
    if scene.saio_scene.scene_type == 'EVR':
        return scene

    result = None
    for bscene in bpy.data.scenes:
        if bscene.saio_scene.scene_type != 'EVR':
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


class EventExporter:

    context: bpy.types.Context
    event_type: str
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
            event_type: str,
            optimize: bool,
            auto_node_attribute_mode: str,
            anim_parameters: AnimParameters):

        self.context = context
        self.event_type = event_type
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
                True,
                False,
                auto_node_attribute_mode,
                False,
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

        for obj in self.base_scene.objects:
            if obj.parent is not None:
                continue

            entry_type = obj.saio_event_entry.entry_type

            if entry_type == "NONE":
                continue
            elif entry_type == "SHADOW":
                self.shadows.append(obj)
            elif entry_type == "REFLECTION":
                self.reflections.append(obj)
            elif entry_type != "PARTICLE":
                self.shared_entries.append(obj)

            self.entry_source_scene[obj] = self.base_scene

        self.shared_entries.sort(key=lambda x: x.name.lower())

        event_properties = self.base_scene.saio_scene.event
        for name in OVERLAY_UPGRADE_LUT.values():
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

            for obj in cutinfo.scene.objects:
                if (obj.parent is not None
                        or obj.name in self.base_scene.objects):
                    continue

                entry_type = obj.saio_event_entry.entry_type

                if entry_type == "PARTICLE":
                    cutinfo.particles.append(obj)
                elif entry_type in ["CHUNK", "GC"]:
                    cutinfo.entries.append(obj)

                    if obj.saio_event_entry.blare:
                        self.blare.append(obj)

                if obj not in self.entry_source_scene:
                    self.entry_source_scene[obj] = cutinfo.scene

            cutinfo.entries.sort(key=lambda x: x.name.lower())
            cutinfo.particles.sort(key=lambda x: x.name.lower())

        if len(self.blare) > 64:
            raise UserException("Can't have more than 64 blare models!")

    ######################################################################

    def _get_children(
            self,
            obj: BObject,
            output: set[BObject]):

        output.add(obj)
        for child in obj.children:
            self._get_children(child, output)

    def _convert_model(self, obj: bpy.types.Object):
        objects = set()
        self._get_children(obj, objects)

        event_props = obj.saio_event_entry
        evaluator = (self.sa2b_evaluator
                     if event_props.entry_type == 'GC'
                     else self.sa2_evaluator)

        # to ensure the correct depsgraph. otherwise triangulating
        # may not always work (or other related functionalities)
        self.context.window.scene = self.entry_source_scene[obj]

        model_data = evaluator.evaluate(objects)

        self.models[obj] = model_data

        nodes = model_data.outdata.GetTreeNodes()
        mapping = model_data.node_data.node_mapping

        for node_source, node_index in mapping.items():
            self.nodes[node_source] = nodes[node_index]

        uv_meshes = []
        for obj in objects:
            uv_anims = obj.saio_eventnode_uvanims
            if len(uv_anims) > 0:
                uv_meshes.append(obj)

        if len(uv_meshes) > 0:
            if event_props.entry_type == 'GC':
                raise UserException(
                    f"Error on {uv_meshes[0].name}:"
                    " GC Models cannot have uv animations")
            elif event_props.entry_type == 'SHADOW':
                raise UserException(
                    f"Error on {uv_meshes[0].name}:"
                    " Shadow models cannot have uv animations")
            elif obj.type == 'ARMATURE':
                raise UserException(
                    f"Error on {uv_meshes[0].name}:"
                    " Armature models do not support uv animations"
                    " (in blender)")

            self.uv_animated_objects.extend(uv_meshes)

    def _convert_models(self):
        base_entries = set()
        base_entries.update(self.shared_entries)
        base_entries.update(self.shadows)
        base_entries.update(self.upgrades)

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
        if self.base_scene.saio_scene.texture_world is None:
            raise UserException("Base scene has no texture list")

        textures = self.base_scene.saio_scene.texture_world.saio_texture_list

        if len(textures) == 0:
            raise UserException(
                "Base scene has no textures in texture list")

        texture_sizes = []

        dimension_type = System.VALUE_TUPLE[System.INT16, System.INT16]

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

            texture_sizes.append(dimension_type(width, height))

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

    def _setup_overlay_upgrades(self):

        event_properties = self.base_scene.saio_scene.event
        for index, name in OVERLAY_UPGRADE_LUT.items():
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
                            "Bone name of overlay upgrade"
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
                        f"Overlay upgrade {name} has targets from different"
                        " entries!")

                root = root1
                if root is None:
                    root = root2
                root_node = self.models[root].outdata

                upgrade_structure = self.event_data.OverlayUpgrades[index]

                upgrade_structure.Root = root_node
                upgrade_structure.Target1 = targets[0]
                upgrade_structure.Model1 = models[0]
                upgrade_structure.Target2 = targets[1]
                upgrade_structure.Model2 = models[1]

                self.event_data.OverlayUpgrades[index] = upgrade_structure

    def _setup_integrated_upgrades(self):

        event_properties = self.base_scene.saio_scene.event

        for index, name in INTEGRATED_UPGRADE_LUT.items():
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
                            "Bone name of integrated upgrade"
                            f" {name}-{fieldname} is empty!")

                    bone = target_object.pose.bones[bone_name]
                    node = self.nodes[bone]
                else:
                    node = self.nodes[target_object]

                # real_index = index * 3 + sub_index
                self.event_data.IntegratedUpgrades[index, sub_index] = node

    def _setup_blare_models(self):

        for index, blare in enumerate(self.blare):
            self.event_data.BlareModels[index] = self.models[blare].outdata

    def _setup_reflection_models(self):
        if len(self.reflections) == 0:
            return

        reflections = SA3D_SA2Event.REFLECTION_DATA()

        for entry in self.reflections:

            if entry.type != "MESH":
                raise UserException(
                    f"Object {entry.name} is a reflection and not a mesh!")

            mesh: bpy.types.Mesh = entry.data
            if len(mesh.vertices) != 4:
                raise UserException(
                    f"Object {entry.name} has more/less than 4 vertices!")

            matrix = entry.matrix_world
            vertices = []

            for vertex in mesh.vertices:
                position = matrix @ vertex.co
                vertices.append(System.VECTOR3(
                    position.x,
                    position.z,
                    -position.y,
                ))

            reflection = SA3D_SA2Event.REFLECTION()
            reflection.Transparency = entry.color[3]
            reflection.Vertex1 = vertices[0]
            reflection.Vertex2 = vertices[1]
            reflection.Vertex3 = vertices[2]
            reflection.Vertex4 = vertices[3]

            reflections.Reflections.Add(reflection)

        self.event_data.Reflections = reflections

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
        uvanim_data = SA3D_SA2Event.SURFACE_ANIMATION_DATA()

        # texture sequences
        for uv_anim in self.base_scene.saio_scene.event.uv_animations:
            texture_sequence = SA3D_SA2Event.TEXTURE_ANIM_SEQUENCE(
                uv_anim.texture_index,
                uv_anim.texture_count)

            uvanim_data.TextureSequences.Add(texture_sequence)

        for uv_animated_object in self.uv_animated_objects:
            node = self.nodes[uv_animated_object]
            block = SA3D_SA2Event.SURFACE_ANIMATION_BLOCK(node)
            uvanim_data.AnimationBlocks.Add(block)

            for anim in uv_animated_object.saio_eventnode_uvanims:

                texture_chunk = SAIO_NET.CUTSCENE.GetTextureChunkFromMaterialIndex(
                    node, anim.material_index)
                texture_index = texture_chunk.TextureID

                block.Animations.Add(SA3D_SA2Event.SURFACE_ANIMATION(
                    texture_index, texture_chunk, None))

        if (uvanim_data.TextureSequences.Count > 0
                or uvanim_data.AnimationBlocks.Count > 0):
            self.event_data.SurfaceAnimations = uvanim_data

    ######################################################################

    def _setup_event_entry(self, obj: BObject):
        from . import o_enum

        entry = SA3D_SA2Event.EVENT_ENTRY()

        properties = obj.saio_event_entry
        if properties.entry_type == 'GC':
            entry.GCModel = self.models[obj].outdata
        else:
            entry.Model = self.models[obj].outdata

        if properties.shadow_model is not None:
            if properties.shadow_model not in self.shadows:
                raise UserException(
                    f"Shadow model \"{properties.shadow_model.name}\" for"
                    f" entry \"{obj.name}\" is not part of the base"
                    " scene and/or not marked to be a shadow model.")
            entry.ShadowModel = self.models[properties.shadow_model].outdata

        entry.Position = System.VECTOR3(
            obj.location.x,
            obj.location.z,
            -obj.location.y,
        )
        entry.Layer = properties.layer

        entry.Attributes = o_enum.to_evententry_attributes(properties)

        return entry

    def _setup_base_scene(self):

        result = SA3D_SA2Event.SCENE(self.total_framecount)
        for obj in self.shared_entries:
            entry = self._setup_event_entry(obj)
            result.Entries.Add(entry)

        return result

    def _setup_animated_scene(self, cutinfo: CutInfo):
        posrot = SA3D_Modeling.KEYFRAME_ATTRIBUTES.Position.op_BitwiseOr(
            SA3D_Modeling.KEYFRAME_ATTRIBUTES.EulerRotation)

        result = SA3D_SA2Event.SCENE(cutinfo.framecount)
        result.BigTheCat = SA3D_SA2Event.BIG_THE_CAT_ENTRY(None, 0)

        result.CameraAnimations.Add(
            SA3D_SA2Event.EVENT_MOTION.CreateFromMotion(cutinfo.camera_motion))

        for obj in cutinfo.entries:
            entry = self._setup_event_entry(obj)

            if obj in cutinfo.motions:
                entry.Animation = cutinfo.motions[obj]
                entry.Animation.EnsureNodeKeyframes(
                    entry.DisplayModel, posrot, True)

            if obj in cutinfo.shape_motions:
                entry.ShapeAnimation = cutinfo.shape_motions[obj]

            entry.AutoAnimationAttributes()
            result.Entries.Add(entry)

        for obj in cutinfo.particles:
            motion = None
            if obj in cutinfo.motions:
                motion = cutinfo.motions[obj]
            motion.EnsureKeyframes(posrot)
            result.ParticleMotions.Add(motion)

        return result

    def _setup_eventdata(self):
        self.event_data = SA3D_SA2Event.MODEL_DATA(o_enum.to_event_type(self.event_type))
        self.event_data.EnableDropShadows = \
            self.base_scene.saio_scene.event.drop_shadow_control

        self._setup_texture_dimensions()
        self._setup_texture_names()
        self._setup_overlay_upgrades()
        self._setup_integrated_upgrades()
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

        textures = None

        if export_textures:
            from . import o_texture
            textures = o_texture.encode_texture_archive(
                o_texture.create_texture_set(
                    self.base_scene.saio_scene.texture_world.saio_texture_list
                ), filepath[:-4] + "texture.prs",
                "GVM"
            )

        event = SA3D_SA2Event.EVENT(
            self.event_data,
            None,
            textures,
            self.event_data.TextureNameList)

        event.WriteToFiles(filepath)
