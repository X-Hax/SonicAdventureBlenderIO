import bpy
from bpy.props import EnumProperty, StringProperty, BoolProperty

from .base_export_operators import (
    ExportOperator,
    AnimationExportOperator,
    NodeAnimExportOperator,
)

from ...exporting import o_motion, o_shapemotion, o_model
from ...utility import camera_utils
from ...exceptions import UserException
from ...dotnet import SA3D_Modeling


class SAIO_OT_Export_Node_Animation(NodeAnimExportOperator):
    bl_idname = "saio.export_node_anim"
    bl_label = "Export Node Animation"
    bl_description = "Export the active armature animation to an SAANIM file"

    @staticmethod
    def _get_action_to_export(context: bpy.types.Context):
        active = context.active_object
        if (active is None or (
                active.type != 'ARMATURE'
                and len(active.children) > 0)):
            return None

        return o_motion.get_action(active, context.scene.frame_current)

    @classmethod
    def poll(cls, context):
        return (
            context.mode in ['OBJECT', 'POSE_ARMATURE']
            and cls._get_action_to_export(context) is not None)

    def export(self, context):

        action = SAIO_OT_Export_Node_Animation._get_action_to_export(context)

        motion = o_motion.convert_to_node_motion(
            context.active_object,
            self.force_sort_bones,
            action.fcurves,
            action.frame_range,
            action.name,
            self.get_anim_parameters()
        )

        SA3D_Modeling.ANIMATION_FILE.WriteToFile(self.filepath, motion)

        return {'FINISHED'}


class SAIO_OT_Export_Node_Animations(NodeAnimExportOperator):
    bl_idname = "saio.export_node_anims"
    bl_label = "Batch Export Node Animations"
    bl_description = "Export the NLA tracks as individual animation files"

    filename_ext = ""

    @classmethod
    def poll(cls, context):
        active = context.active_object
        return (
            context.mode in ['OBJECT', 'POSE_ARMATURE']
            and active is not None
            and (active.type == 'ARMATURE'
                 or len(active.children) == 0)
            and active.animation_data is not None
            and len(active.animation_data.nla_tracks) > 0)

    def export(self, context: bpy.types.Context):
        import os
        active = context.active_object
        folder = os.path.dirname(os.path.abspath(self.filepath))
        anim_parameters = self.get_anim_parameters()

        for nla_track in active.animation_data.nla_tracks:
            if len(nla_track.strips) == 0:
                continue

            for strip in nla_track.strips:
                if strip.type != "CLIP" or strip.action is None:
                    continue

                outpath = os.path.join(
                    folder, f"{strip.action.name}.saanim")

                motion = o_motion.convert_to_node_motion(
                    active,
                    self.force_sort_bones,
                    strip.action.fcurves,
                    (strip.action_frame_start, strip.action_frame_end),
                    strip.name,
                    anim_parameters
                )

                SA3D_Modeling.ANIMATION_FILE.WriteToFile(outpath, motion)

        return {'FINISHED'}


class SAIO_OT_Export_Camera_Animation(AnimationExportOperator):
    bl_idname = "saio.export_camera_anims"
    bl_label = "Export Camera Animation"
    bl_description = "Export the active camera animation"

    filename_ext = ".saanim"

    camera_setup: camera_utils.CameraSetup
    action_setup: camera_utils.CameraActionSet | None
    motion_name: str

    @staticmethod
    def _get_action_setup(camera_setup: camera_utils.CameraSetup, frame: int):
        if camera_setup is None:
            return None

        # priority row: position -> target+roll -> fov
        id_data = (
            camera_setup.camera,
            camera_setup.target,
            camera_setup.camera_data)

        action = None
        postfix = None
        for idd, postfix in zip(id_data, camera_utils.ACTION_POSTFIX):
            action = o_motion.get_action(idd, frame)
            if action is not None:
                break

        if action is None:
            return None

        if not action.name.endswith(postfix):
            raise UserException(
                f"Action \"{action.name}\" is a {postfix[1:]} action and it's"
                f" name has to end with \"{postfix}\" to be recognized as"
                " such, otherwise the other actions cannot be found!")

        name = action.name[:-len(postfix)]

        actions = []
        for postfix in camera_utils.ACTION_POSTFIX:
            index = bpy.data.actions.find(name + postfix)
            if index == -1:
                actions.append(None)
            else:
                actions.append(bpy.data.actions[index])

        return camera_utils.CameraActionSet(
            actions[0],
            actions[1],
            actions[2],
        )

    @classmethod
    def poll(cls, context):
        if context.mode != 'OBJECT':
            return False

        camera_setup = camera_utils.CameraSetup.get_setup(
            context.active_object)
        try:
            return cls._get_action_setup(
                camera_setup, context.scene.frame_current) is not None
        except UserException:
            return True

    def _invoke(self, context, event):
        self.camera_setup = camera_utils.CameraSetup.get_setup(
            context.active_object)
        self.action_setup = self._get_action_setup(
            self.camera_setup, context.scene.frame_current)

        for action, postfix in zip(
                self.action_setup.as_list(),
                camera_utils.ACTION_POSTFIX):
            if action is not None:
                self.motion_name = action.name[:-len(postfix)]
                break

        return super()._invoke(context, event)

    def draw(self, context: bpy.types.Context):
        self.draw_panel_info(self.layout)
        super().draw(context)

    def draw_panel_info(self, layout: bpy.types.UILayout):
        header, body = layout.panel(
            "SAIO_export_camanim_info", default_closed=False)
        header.label(text="Info")

        if body:
            body.label(text=f"Action to export: {self._actions.name}")
            body.label(text="Using:")

            for action, postfix in zip(
                    self.action_setup.as_list(),
                    camera_utils.ACTION_POSTFIX):

                found = "Found" if action is not None else "Missing"
                body.label(text=f"{self.motion_name}{postfix} [{found}]")

        return body

    def export(self, context: bpy.types.Context):

        motion = o_motion.convert_to_camera_motion(
            self.camera_setup,
            self.action_setup,
            self.motion_name,
            self.get_anim_parameters(),
        )

        SA3D_Modeling.ANIMATION_FILE.WriteToFile(self.filepath, motion)

        return {'FINISHED'}


class SAIO_OT_Export_Shape_Animation(ExportOperator):
    bl_idname = "saio.export_shape_anims"
    bl_label = "Export Shape Animation"
    bl_description = "Export the active shape animation"

    filename_ext = ".saanim"

    filter_glob: StringProperty(
        default="*.saanim;",
        options={'HIDDEN'},
    )

    normal_mode: EnumProperty(
        name="Normal mode",
        description=(
            "Whether and how normals should be added to the shape motion"
        ),
        items=(
            ("NONE", "None", "No normal keyframes at all"),
            ("TYPED", "Typed", "Will be formatted to read as \"has normals\","
                               " but contains no actual normals data"),
            ("NULLED", "Nulled", "Add keyframes with a single Zero vector"),
            ("FULL", "Full", "Add normal keyframes")
        ),
        default="TYPED"
    )

    force_sort_bones: BoolProperty(
        name="Force sort bones",
        description=(
            "Blender doesnt sort bones by name, although this may be desired"
            " in certain scenarios. This ensure the bones are sorted by name"),
        default=False
    )

    _actions: o_shapemotion.ShapeActionCollection | None

    @classmethod
    def poll(cls, context):
        if context.mode != 'OBJECT' or context.active_object is None:
            return False
        try:
            return o_shapemotion.ShapeActionCollector.collect_shape_actions(
                context.active_object, context.scene.frame_current) is not None
        except UserException:
            # returning true on error so that the user can click and get the
            # exception on invoke to know what is wrong
            return True

    def _invoke(self, context: bpy.types.Context, event):
        sac = o_shapemotion.ShapeActionCollector
        try:
            self._actions = sac.collect_shape_actions(
                context.active_object, context.scene.frame_current)
        except UserException as e:
            self.report({'ERROR'}, e.message)
            return {'CANCELLED'}

        for obj, action in self._actions.actions.items():
            self._actions.name = action.name[:-(1 + len(obj.name))]
            break

        return super()._invoke(context, event)

    def draw(self, context):
        super().draw(context)
        layout = self.layout

        self.draw_panel_info(layout)
        self.draw_panel_general(layout)

    def draw_panel_info(self, layout: bpy.types.UILayout):
        header, body = layout.panel(
            "SAIO_export_shapeanim_info", default_closed=False)
        header.label(text="Info")

        if body:
            body.label(text=f"Action to export: {self._actions.name}")
            body.label(text="Using:")

            for obj, action in self._actions.actions.items():
                layout.label(text=f"\"{action.name}\" for \"{obj.name}\"")

        return body

    def draw_panel_general(self, layout: bpy.types.UILayout):
        header, body = layout.panel(
            "SAIO_export_shapeanim_general", default_closed=True)
        header.label(text="General")

        if body:
            body.prop(self, "normal_mode")
            body.prop(self, "force_sort_bones")

        return body

    def export(self, context: bpy.types.Context):
        objects = {context.active_object}
        objects.update(context.active_object.children_recursive)

        model_eval = o_model.ModelEvaluator(
            context,
            None,
            force_sort_bones=self.force_sort_bones)
        model_data = model_eval.evaluate(objects, False)

        evaluator = o_shapemotion.ShapeMotionEvaluator(
            model_data,
            context,
            self.normal_mode)

        motion = evaluator.evaluate(self._actions)
        SA3D_Modeling.ANIMATION_FILE.WriteToFile(self.filepath, motion)
        return {'FINISHED'}
