import os
import bpy
from bpy.props import (
    BoolProperty,
    StringProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty
)

from .base import SAIOBaseFileLoadOperator
from ...dotnet import load_dotnet, SA3D_Modeling
from ...utility import bone_utils, camera_utils
from ...utility.general import target_anim_editor
from ...utility.draw import expand_menu
from ...importing import i_motion


class MotionImportOperator(SAIOBaseFileLoadOperator):
    bl_options = {'PRESET', 'UNDO'}

    filter_glob: StringProperty(
        default="*.saanim;*.njm",
        options={'HIDDEN'},
    )

    files: CollectionProperty(
        name='File paths',
        type=bpy.types.OperatorFileListElement
    )


class SAIO_OT_Import_Node_Animation(MotionImportOperator):
    bl_idname = "saio.import_node_anim"
    bl_label = "Import Node Animation"
    bl_description = "Loads SAANIM files to a selected armature"

    rotation_mode: EnumProperty(
        name="Rotation Mode",
        description="How rotations should be imported",
        items=(
            ("ANIM", "Animation", "Adjust bone rotation modes to match the"
             " animation"),
            ("KEEP", "Keep", "Import into bone rotation modes"),
        ),
        default="ANIM"
    )

    quaternion_threshold: FloatProperty(
        name="Quaternion conversion deviation threshold",
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
        default=0,
        min=0
    )

    short_rot: BoolProperty(
        name="Read as 16 bit rotations",
        description=(
            "Fallback value. Only required to be set if the file version is 0"
        ),
        default=False
    )

    show_advanced: BoolProperty(
        name="Advanced",
        default=False
    )

    @classmethod
    def poll(cls, context):
        active = context.active_object
        return (
            context.mode == 'OBJECT'
            and active is not None and (
                active.type == 'ARMATURE'
                or len(active.children) == 0
            ))

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        layout.prop(self, "rotation_mode")

        box = layout.box()
        if expand_menu(box, self, "show_advanced"):
            box.prop(self, "quaternion_threshold")
            box.prop(self, "short_rot")

    def _execute(self, context):
        directory = os.path.dirname(self.filepath)

        load_dotnet()

        node_num = 1
        if context.active_object.type == "ARMATURE":
            node_num = len(bone_utils.get_bone_map(
                context.active_object, False, False))

        if context.active_object.animation_data is None:
            context.active_object.animation_data_create()

        for file in self.files:

            filepath = os.path.join(directory, file.name)
            try:
                animFile = SA3D_Modeling.ANIMATION_FILE.ReadFromFile(
                    filepath, node_num, self.short_rot)
            except Exception as error:
                print(f"An error occured while importing {file.name}")
                raise error

            action = i_motion.NodeMotionProcessor.process_motion(
                animFile.Animation,
                context.active_object,
                self.rotation_mode,
                self.quaternion_threshold)

            nla_track = context.active_object.animation_data.nla_tracks.new()
            nla_track.name = os.path.splitext(file.name)[0]
            nla_track.strips.new(action.name, 0, action)

        nla_track.is_solo = True

        try:
            target_anim_editor(context)
        except Exception:
            context.active_object.animation_data.use_tweak_mode = False
            context.active_object.animation_data.action = action

        return {'FINISHED'}


class SAIO_OT_Import_Camera_Animation(MotionImportOperator):
    bl_idname = "saio.import_camera_anim"
    bl_label = "Import Camera Animation"
    bl_description = "Loads SAANIM files to a selected camera setup"

    @classmethod
    def poll(cls, context):
        return (
            context.mode == 'OBJECT'
            and camera_utils.CameraSetup.get_setup(
                context.active_object) is not None)

    def _execute(self, context):
        directory = os.path.dirname(self.filepath)
        camera_setup = camera_utils.CameraSetup.get_setup(
            context.active_object)

        load_dotnet()

        def setup_animdata(data: bpy.types.ID):
            if data.animation_data is None:
                data.animation_data_create()

        setup_animdata(camera_setup.camera)
        setup_animdata(camera_setup.target)
        setup_animdata(camera_setup.camera_data)

        for file in self.files:

            filepath = os.path.join(directory, file.name)
            try:
                animFile = SA3D_Modeling.ANIMATION_FILE.ReadFromFile(filepath, 1, False)
            except Exception as error:
                print(f"An error occured while importing {file.name}")
                raise error

            actions = i_motion.CameraMotionProcessor.process_motion(
                animFile.Animation,
                camera_setup)

            def setup_nla(data: bpy.types.ID, action: bpy.types.Action):
                track = data.animation_data.nla_tracks.new()
                track.name = os.path.splitext(file.name)[0]
                track.strips.new(action.name, 0, action)

            setup_nla(camera_setup.camera, actions.position)
            setup_nla(camera_setup.target, actions.target)
            setup_nla(camera_setup.camera_data, actions.fov)

        return {'FINISHED'}


class SAIO_OT_Import_Shape_Animation(MotionImportOperator):
    bl_idname = "saio.import_shape_anim"
    bl_label = "Import Shape Animation"
    bl_description = "Loads shape animations files to a selected armature"

    optimize: BoolProperty(
        name="Optimize",
        description="Merge shape motions that are nearly identical",
        default=True
    )

    @classmethod
    def poll(cls, context):
        active = context.active_object
        return (
            context.mode == 'OBJECT'
            and active is not None and (
                active.type == 'ARMATURE'
                or len(active.children) == 0
            ))

    def _execute(self, context):
        directory = os.path.dirname(self.filepath)

        load_dotnet()

        node_num = 1
        if context.active_object.type == "ARMATURE":
            node_num = len(bone_utils.get_bone_map(
                context.active_object, False, True))

        for file in self.files:

            filepath = os.path.join(directory, file.name)
            try:
                animFile = SA3D_Modeling.ANIMATION_FILE.ReadFromFile(filepath, node_num, False)
            except Exception as error:
                print(f"An error occured while importing {file.name}")
                raise error

            processor = i_motion.ShapeMotionProcessor(self.optimize)
            actions = processor.process(animFile.Animation, context.active_object)

            for target, action in actions.items():
                shape_keys: bpy.types.Key = target.data.shape_keys
                if shape_keys.animation_data is None:
                    shape_keys.animation_data_create()
                nla = shape_keys.animation_data.nla_tracks.new()
                nla.strips.new(action.name, 0, action)

        return {'FINISHED'}
