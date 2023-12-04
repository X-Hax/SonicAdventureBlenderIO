import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty
)
from bpy.types import Context
import mathutils

from .base import SAIOBaseOperator, SAIOBasePopupOperator
from .anim_export_operators import SAIO_OT_Export_Node_Animation

from ..property_groups.node_properties import SAIO_Node

from ...utility.draw import expand_menu
from ...utility.general import target_anim_editor
from ...exceptions import SAIOException
from ...dotnet import load_dotnet, TextCopy


class SAIO_OT_TestBakeAnimation(SAIOBaseOperator):
    bl_idname = "saio.tool_testbakeanim"
    bl_label = "Bake Node Animation"
    bl_description = (
        "Simulates export and import in a fast step to preview the resulting"
        " action"
    )
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}

    out_bone_localspace: BoolProperty(
        name="Bone Localspace",
        description=(
            "When exporting the animation,"
            " ignore the armature object position"),
        default=True
    )

    out_short_rot: BoolProperty(
        name="Use 16 bit rotations",
        description="Whether to use 16 bit BAMS for the rotation keyframes",
        default=False
    )

    out_rotation_mode: EnumProperty(
        name="Rotation Mode",
        description="How rotations should be exported",
        items=(
            ("EULER", "Euler", "Export rotations as euler"
                " (sonic adventure compatible)"),
            ("QUATERNION", "Quaternion", "Export rotations as quaternion"
                " (compatible with games like PSO2)"),
            ("KEEP", "Keep",
                "Import into bone rotation modes"),
        ),
        default="EULER"
    )

    out_ensure_positive_euler_angles: BoolProperty(
        name="Ensure positive euler angles",
        description="Ensure that all exported euler rotation angles are positive.",
        default=True
    )

    out_interpolation_threshold: FloatProperty(
        name="Interpolation conversion deviation threshold",
        description=(
            "Keyframes between non linear keyframes need to be baked for"
            " export. This factor determines that, if a keyframes deviates"
            " less than the given value from its linear interpolated"
            " counterpart, it will be removed."

            "\n0 is gonna bake every value (except for keyframes using linear"
            " or constant interpolation)."

            "\nDoes not affect manually placed keyframes"
        ),
        min=0,
        default=0.05,
    )

    out_quaternion_threshold: FloatProperty(
        name="Quaternion conversion deviation threshold",
        description=(
            "If the animations rotation data doesnt match the export"
            " rotation mode, the data will have to be converted. converting"
            " between euler and quaternion rotations is inaccurate, as the"
            " interpolation between those types is not linear. This value"
            " determines the threshold, from which a keyframe should be"
            " removed."

            "\n0 means all interpolated keyframes, 1 means none."

            "\nUsually, a value around 0.05 is enough and gets rid of most"
            " unnecessary keyframes."

            "\nDoes not affect keyframes determined by the addon"
        ),
        min=0,
        max=1,
        default=0.05
    )

    out_general_optim_thresh: FloatProperty(
        name="Optimization deviation threshold",
        description=(
            "Utilized for optimization of all but rotations. If a keyframe"
            " deviates less than the threshold from its linear interpolated"
            " counterpart, it will be removed."

            "\n0 will not optimize at all"

            "\nAffects all frames"
        ),
        min=0,
        default=0.05
    )

    out_quaternion_optim_thresh: FloatProperty(
        name="Quaternion Optimization deviation threshold",
        description=(
            "Utilized for optimization of rotations. If a keyframe deviates"
            " less than the threshold from its linear interpolated"
            " counterpart, it will be removed."

            "\n0 will not optimize at all"

            "\nAffects all frames"
        ),
        min=0,
        default=0.01
    )

    out_show_advanced: BoolProperty(
        name="Advanced",
        default=False
    )

    in_rotation_mode: EnumProperty(
        name="Rotation Mode",
        description="How rotations should be imported",
        items=(
            ("ANIM", "Animation", "Adjust bone rotation modes to match the"
             " animation"),
            ("KEEP", "Keep", "Import into bone rotation modes"),
        ),
        default="ANIM"
    )

    in_quaternion_threshold: FloatProperty(
        name="Quaternion conversion deviation",
        description=(
            "If the animations rotation data doesnt match the bones"
            " rotation mode, the data will have to be converted. converting"
            " between euler and quaternion rotations is inaccurate, as the"
            " interpolation between those types is not linear. This value"
            " determines the threshold, from which a keyframe should be"
            " removed. 0 means all interpolated keyframes, 1 means none."
            " usually, a value around 0.05 is enough and gets rid of most"
            " unnecessary keyframes"
        ),
        default=0.05,
        min=0,
        max=1
    )

    in_show_advanced: BoolProperty(
        name="Advanced",
        default=False
    )

    @classmethod
    def poll(cls, context):
        return SAIO_OT_Export_Node_Animation.poll(context)

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        layout.label(text="Export properties")

        layout.prop(self, "out_bone_localspace")
        layout.prop(self, "out_short_rot")
        layout.prop(self, "out_ensure_positive_euler_angles")

        box = layout.box()
        if expand_menu(box, self, "out_show_advanced"):
            box.prop(self, "out_rotation_mode")
            box.prop(self, "out_interpolation_threshold")
            box.prop(self, "out_quaternion_threshold")
            box.prop(self, "out_general_optim_thresh")
            box.prop(self, "out_quaternion_optim_thresh")

        layout.separator(factor=2)
        layout.label(text="Import properties")

        layout.prop(self, "in_rotation_mode")

        box = layout.box()
        if expand_menu(box, self, "in_show_advanced"):
            box.prop(self, "in_quaternion_threshold")

    def _execute(self, context: bpy.types.Context):
        from ...exporting import o_motion
        from ...importing import i_motion
        from ...utility import anim_parameters
        from ...dotnet import SA3D_Modeling

        armature_object = context.active_object

        out_action = o_motion.get_action(
            armature_object,
            context.scene.frame_current)

        out_anim_parameters = anim_parameters.AnimParameters(
            self.out_bone_localspace,
            self.out_rotation_mode,
            self.out_interpolation_threshold,
            self.out_quaternion_threshold,
            self.out_general_optim_thresh,
            self.out_quaternion_optim_thresh,
            self.out_short_rot,
            self.out_ensure_positive_euler_angles
        )

        out = o_motion.convert_to_node_motion(
            context.active_object,
            False,
            out_action.fcurves,
            out_action.frame_range,
            out_action.name,
            out_anim_parameters
        )

        # emulating file export and import
        file_bytes = SA3D_Modeling.ANIMATION_FILE.WriteToBytes(out)
        in_motion = SA3D_Modeling.ANIMATION_FILE.ReadFromBytes(
            file_bytes).Animation

        in_action = i_motion.NodeMotionProcessor.process_motion(
            in_motion,
            armature_object,
            False,
            self.in_rotation_mode,
            self.in_quaternion_threshold
        )

        track = armature_object.animation_data.nla_tracks.new()
        track.name = "BakeTest_" + in_action.name
        track.strips.new(in_action.name, 0, in_action)

        track.is_solo = True

        try:
            target_anim_editor(context)
        except Exception:
            context.active_object.animation_data.use_tweak_mode = False
            context.active_object.animation_data.action = in_action

        return {'FINISHED'}


class SAIO_OT_ArmatureFromObjects(SAIOBasePopupOperator):
    ('''Generates an armature based on the selected node and its child'''
     ''' hierarchy''')

    bl_idname = "saio.tool_armaturefromobjects"
    bl_label = "Armature from objects"
    bl_description = (
        "Generate an armature from object. Select the parent of all objects,"
        " which will represent the root"
    )
    bl_options = {'UNDO'}

    rotation_mode: EnumProperty(
        name="Rotation Mode",
        description="The rotation mode of each bone in the generated armature",
        items=(('QUATERNION', "Quaternion (WXYZ)", "No Gimbal Lock."),
               ('XYZ', "XYZ Euler", "XYZ Euler - prone to Gimbal Lock."),
               ('XZY', "XZY Euler", "XZY Euler - prone to Gimbal Lock."),
               ('YXZ', "YXZ Euler", "YXZ Euler - prone to Gimbal Lock."),
               ('YZX', "YZX Euler", "YZX Euler - prone to Gimbal Lock."),
               ('ZXY', "ZXY Euler", "ZXY Euler - prone to Gimbal Lock."),
               ('ZYX', "ZYX Euler", "ZYX Euler - prone to Gimbal Lock.")),
        default='XYZ'
    )

    merge_meshes: BoolProperty(
        name="Merge Meshes",
        description=(
            "Generates a single mesh object instead of keeping the single"
            " objects"
        ),
        default=False
    )

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return (
            context.mode == 'OBJECT'
            and context.active_object is not None
            and context.active_object.type != 'ARMATURE'
        )

    @staticmethod
    def add_children(
            parent: bpy.types.Object,
            result: list[bpy.types.Object],
            resultMeshes: list[bpy.types.Object]):

        result.append(parent)
        if parent.type == 'MESH':
            resultMeshes.append(parent)

        children: list[bpy.types.Object] = [child for child in parent.children]
        children.sort(key=lambda x: x.name)

        for child in children:
            SAIO_OT_ArmatureFromObjects.add_children(
                child, result, resultMeshes)

    def _execute(self, context: bpy.types.Context):
        root_object = context.active_object

        objects: list[bpy.types.Object] = []
        meshes: list[bpy.types.Object] = []

        SAIO_OT_ArmatureFromObjects.add_children(
            root_object, objects, meshes)

        if len(objects) == 1:
            return {'CANCELLED'}

        from ...exporting.o_node import NodeEvaluator

        evaluator = NodeEvaluator(context, False, False, True, True)
        structure = evaluator.evaluate(objects)

        # creating a fake SAIO Node hierarchy to use in the
        # armature_from_node_tree function

        fake_nodes: list['FakeNode'] = []

        class FakeTuple:
            Item1: any
            Item2: any

            def __init__(self, item1, item2):
                self.Item1 = item1
                self.Item2 = item2


        class FakeNode:

            Name: str
            Attributes: any
            Parent: 'FakeNode'
            IsVirtualRoot: bool
            matrices: list[FakeTuple]

            def __init__(self, node):
                self.Label = node.Label
                self.Attributes = node.Attributes
                self.IsVirtualRoot = False

                if node.ParentIndex >= 0:
                    self.Parent = fake_nodes[node.ParentIndex]
                else:
                    self.Parent = None

            def GetWorldMatrixTree(self):
                return self.matrices

        from ...exporting import o_matrix
        matrices = []
        for index, node in enumerate(structure.nodes):
            fake_node = FakeNode(node)
            fake_nodes.append(fake_node)
            matrices.append(FakeTuple(
                fake_node,
                o_matrix.bpy_to_net_matrix(objects[index].matrix_world)
            ))

        fake_nodes[0].matrices = matrices

        name_map = {}
        for index, obj in enumerate(objects):
            name_map[obj.name] = index

        from ...importing.i_node import NodeProcessor
        from ...importing.i_mesh import MeshData

        collection = root_object.users_collection[0]

        processor = NodeProcessor(
            context,
            collection,
            False,
            self.merge_meshes
        )

        for index, mesh in enumerate(meshes):
            mesh_data = MeshData(0, [name_map[mesh.name]])
            mesh_data.mesh = mesh.data
            processor.meshes.append(mesh_data)

        processor.process_as_armature(fake_nodes, collection.name)

        return {'FINISHED'}


class SAIO_OT_ArmaturCorrectVisual(SAIOBasePopupOperator):
    bl_idname = "saio.tool_armaturecorrectvisual"
    bl_label = "Correct Armature Visuals"
    bl_description = (
        "Assigns bone shapes to the bones as well as other features that are"
        " helpful when working with the armature"
    )
    bl_options = {'UNDO'}

    bone_shapes: BoolProperty(
        name="Bone Shapes",
        description="Assigns each bone a shape to display the rotations in a more \"correct\" way",
        default=True
    )

    bone_groups: BoolProperty(
        name="Bone Groups",
        description="Assign each bone a bone group based on how they affect the meshes",
        default=True
    )

    bone_colors: BoolProperty(
        name="Bone Colors",
        description="Assign each bone a distinct color based on how they affect the meshes",
        default=True
    )

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return (
            context.mode in ['OBJECT', 'POSE_ARMATURE']
            and context.active_object is not None
            and context.active_object.type == 'ARMATURE'
        )

    @staticmethod
    def _get_shape_object(context: bpy.types.Context):
        from ...utility import general
        general.load_template_blend(context)

        for obj in bpy.data.objects:
            if (obj.name.startswith("SAIO Bone Shape")
                    and general.is_from_template(obj)):
                return obj

        raise SAIOException("Bone shape not found")

    @staticmethod
    def _set_bone_shapes(
            context: bpy.types.Context,
            armature_obj: bpy.types.Object):
        bone_shape = SAIO_OT_ArmaturCorrectVisual._get_shape_object(context)

        for b in armature_obj.pose.bones:
            b.custom_shape = bone_shape

    @staticmethod
    def _eval_bone_groupings(armature_obj: bpy.types.Object):
        from ...utility.general import get_armature_modifier

        groupings: dict[str, list[str]] = {}

        for bone in armature_obj.pose.bones:
            groupings[bone.name] = []

        mesh_groups: dict[str, list] = {}

        for mesh_obj in armature_obj.children:
            mesh_groups[mesh_obj.name] = []

            if get_armature_modifier(mesh_obj) is not None:
                for group in mesh_obj.vertex_groups:
                    if group.name not in groupings:
                        continue
                    groupings[group.name].append(mesh_obj.name)

            elif mesh_obj.parent_type == 'BONE':
                groupings[mesh_obj.parent_bone].append(None)

        no_effect = []
        is_parent = []
        multi = []

        for bonename, grouping in groupings.items():
            if len(grouping) == 0:
                no_effect.append(bonename)
                continue
            elif len(grouping) > 1:
                multi.append(bonename)

            for group in grouping:
                if group is None:
                    is_parent.append(bonename)
                else:
                    mesh_groups[group].append(bonename)

        for mesh_name in list(mesh_groups.keys()):
            if len(mesh_groups[mesh_name]) == 0:
                del mesh_groups[mesh_name]

        return (no_effect, is_parent, multi, mesh_groups)

    @staticmethod
    def _setup_bone_collections(
            armature_obj: bpy.types.Object,
            groupings: tuple[list, list, list, dict[str, list]]):

        armature: bpy.types.Armature = armature_obj.data

        def create_collection(name: str, bonenames: list[str]):
            if len(bonenames) == 0:
                return

            collection = armature.collections.new(name)
            for bonename in bonenames:
                collection.assign(armature.bones[bonename])

        create_collection("Empty", groupings[0])
        create_collection("Is Parent", groupings[1])
        create_collection("Multiple", groupings[2])
#
        for mesh_name, bonenames in groupings[3].items():
            create_collection(mesh_name, bonenames)

    @staticmethod
    def _setup_bone_colors(
            armature_obj: bpy.types.Object,
            groupings: tuple[list, list, list, dict[str, list]]):

        armature: bpy.types.Armature = armature_obj.data

        mesh_themes = [
            "THEME09",
            "THEME04",
            "THEME03",
            "THEME06",
            "THEME02",
            "THEME07",
            "THEME08",
            "THEME14",
            "THEME12",
            "THEME15",
        ]

        for i, bonenames in enumerate(groupings[3].values()):
            mesh_theme = mesh_themes[i % len(mesh_themes)]

            for bonename in bonenames:
                armature.bones[bonename].color.palette = mesh_theme

        for bonename in groupings[0]:
            armature.bones[bonename].color.palette = "THEME13"

        for bonename in groupings[1]:
            armature.bones[bonename].color.palette = "THEME11"

        for bonename in groupings[2]:
            armature.bones[bonename].color.palette = "THEME01"

    def _execute(self, context: bpy.types.Context):

        armature_obj = context.active_object

        if self.bone_shapes:
            SAIO_OT_ArmaturCorrectVisual._set_bone_shapes(
                context, armature_obj)

        if self.bone_groups or self.bone_colors:
            groupings = SAIO_OT_ArmaturCorrectVisual._eval_bone_groupings(
                armature_obj)

            if self.bone_groups:
                SAIO_OT_ArmaturCorrectVisual._setup_bone_collections(
                    armature_obj, groupings)

            if self.bone_colors:
                SAIO_OT_ArmaturCorrectVisual._setup_bone_colors(
                    armature_obj, groupings)

        return {'FINISHED'}


class SAIO_OT_SetupCamera(SAIOBaseOperator):
    bl_idname = "saio.tool_setupcamera"
    bl_label = "Create a camera setup"
    bl_description = "Create a camera setup that accepts camera animations"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.mode == 'OBJECT'

    def _execute(self, context: bpy.types.Context):
        collection = bpy.data.collections.new(context.scene.name + "_camera")
        bpy.context.scene.collection.children.link(collection)

        from ...utility.camera_utils import CameraSetup
        CameraSetup.create_setup(context.scene.name, collection, False)
        return {'FINISHED'}


class SAIO_OT_CopyVertexIndicesToClipboard(SAIOBaseOperator):
    bl_idname = "saio.tool_vertexid_clipboard"
    bl_label = "Copy Vertex indices to clipboard"
    bl_description = (
        "Copies the indices of the selected vertices to the clipboard"
    )

    @classmethod
    def poll(cls, context: Context):
        return (
            context.active_object is not None
            and context.active_object.type == 'MESH'
            and context.active_object.data.total_vert_sel > 0)

    def _execute(self, context: bpy.types.Context):
        context.active_object.update_from_editmode()

        text = ""

        for vert in context.active_object.data.vertices:
            if vert.select:
                text += str(vert.index) + ","

        text = text[:-1]

        load_dotnet()

        TextCopy.CLIPBOARD_SERVICE.SetText(text)

        return {'FINISHED'}


class SAIO_OT_AutoNodeAttributes(SAIOBasePopupOperator):
    bl_idname = "saio.tool_autonodeattrib"
    bl_label = "Auto Node Attributes"
    bl_description = (
        "Automatically determines Node attrbiutes for selected objects"
    )
    bl_options = {'UNDO'}

    mode: EnumProperty(
        name="Mode",
        items=(
            ("ALL", "All", "Calculate flags for all objects in the file"),
            ("SCENE", "Scene",
                "Calculate flags for all objects in the active scene"),
            ("VISIBLE", "Visible", "Visible objects only"),
            ("SELECTED", "Selected", "Calculate flags for selected objects")
        ),
        default="SCENE"
    )

    def _get_objects(self, context: Context):

        source = context.scene.objects

        if self.mode == 'VISIBLE':
            def check(x: bpy.types.Object):
                return not x.hide_get()
        elif self.mode == 'SELECTED':
            def check(x: bpy.types.Object):
                return x.select_get()
        else:
            def check(x: bpy.types.Object):  # pylint: disable=unused-argument
                return True

            if self.mode == 'ALL':
                source = bpy.data.objects

        return [obj for obj in source if check(obj)]

    def _calc_node_flags(self, target: bpy.types.Object | bpy.types.Bone):

        if isinstance(target, bpy.types.Bone):
            matrix = target.matrix_local
            if target.parent is not None:
                matrix = target.parent.matrix_local.inverted() @ matrix

            location, rotation, _ = matrix.decompose()
            scale = mathutils.Vector((1, 1, 1))  # Non-pose scale doesnt exist
            rotation = rotation.to_euler()

        else:
            location = target.location
            scale = target.scale
            if target.rotation_mode == 'QUATERNION':
                rotation = target.rotation_quaternion.to_euler()
            else:
                rotation = target.rotation_euler

        node_properties: SAIO_Node = target.saio_node

        node_properties.ignore_position = location.length == 0

        node_properties.ignore_rotation = (
            rotation.x == 0 and rotation.y == 0 and rotation.z == 0)

        node_properties.ignore_scale = (
            scale.x == 1 and scale.y == 1 and scale.z == 1)

        node_properties.skip_children = len(target.children) == 0

    @classmethod
    def poll(cls, context: Context):
        return context.mode == 'OBJECT'

    def _execute(self, context: Context):

        objects = self._get_objects(context)
        if len(objects) == 0:
            return {'FINISHED'}

        for obj in objects:
            self._calc_node_flags(obj)

            if obj.type == 'ARMATURE':
                bpy.ops.object.mode_set(mode='POSE')
                prev = context.view_layer.objects.active
                context.view_layer.objects.active = obj
                for bone in obj.data.bones:
                    self._calc_node_flags(bone)
                bpy.ops.object.mode_set(mode='OBJECT')
                context.view_layer.objects.active = prev

        return {'FINISHED'}
