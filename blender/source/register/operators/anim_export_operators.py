import bpy
from bpy.props import EnumProperty, StringProperty, BoolProperty

from .base_export_operators import (
    ExportOperator,
    AnimationExportOperator,
    NodeAnimExportOperator,
)

from ...exporting.o_motion import ActionSet

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

        return ActionSet.from_data(active, context.scene.frame_current)

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
            action,
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
                    strip.action,
                    anim_parameters,
                    frame_range=(strip.action_frame_start, strip.action_frame_end)
                )

                SA3D_Modeling.ANIMATION_FILE.WriteToFile(outpath, motion)

        return {'FINISHED'}


class SAIO_OT_Export_Camera_Animation(AnimationExportOperator):
    bl_idname = "saio.export_camera_anims"
    bl_label = "Export Camera Animation"
    bl_description = "Export the active camera animation"

    filename_ext = ".saanim"

    camera_setup: camera_utils.CameraSetup
    camera_action: camera_utils.CameraAction | None

    @staticmethod
    def _get_action_setup(camera_setup: camera_utils.CameraSetup, frame: int):
        if camera_setup is None:
            return None

        # priority row: position -> target+roll -> fov
        id_data = (
            camera_setup.camera,
            camera_setup.target,
            camera_setup.camera_data
        )

        actions = [ActionSet.from_data(idd, frame) for idd in id_data]

        base_action = None
        for action in actions:
            if action is None:
                continue

            if base_action is None:
                base_action = action
            elif action != base_action:
                raise UserException(
                    "The active camera setup uses more than 1 action!\n",
                    "Please ensure that the camera object, target object and"
                    " camera data all use slots on the same action"
                )

        if base_action is None:
            return None

        return camera_utils.CameraAction(
            base_action,
            actions[0].slot if actions[0] is not None else None,
            actions[1].slot if actions[1] is not None else None,
            actions[2].slot if actions[2] is not None else None,
        )

    @classmethod
    def poll(cls, context):
        if context.mode != 'OBJECT':
            return False

        camera_setup = camera_utils.CameraSetup.get_setup(context.active_object)

        try:
            return cls._get_action_setup(
                camera_setup, context.scene.frame_current) is not None
        except UserException:
            return True

    def _invoke(self, context, event):
        self.camera_setup = camera_utils.CameraSetup.get_setup(
            context.active_object
        )
        
        self.camera_action = self._get_action_setup(
            self.camera_setup, 
            context.scene.frame_current
        )

        return super()._invoke(context, event)

    def draw(self, context: bpy.types.Context):
        self.draw_panel_info(self.layout)
        super().draw(context)

    def draw_panel_info(self, layout: bpy.types.UILayout):
        header, body = layout.panel(
            "SAIO_export_camanim_info", default_closed=False)
        header.label(text="Info")

        if body:
            body.label(text=f"Action to export: {self.camera_action.action.name}")

        return body

    def export(self, context: bpy.types.Context):

        motion = o_motion.convert_to_camera_motion(
            self.camera_setup,
            self.camera_action,
            self.camera_action.action.name,
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

    attach_format: EnumProperty(
        name="Attach format",
        description=(
            "Attach format, for which the shape animation is exported"
            " (needed to correctly map vertex numbers)"),
        items=(
            ('SA1', "SA1", "SA1MDL export format"),
            ('SA2', "SA2", "SA2MDL export format"),
            ('SA2B', "SA2B", "SA2BMDL export format"),
        ),
        default="SA1"
    )

    optimize: BoolProperty(
        name="Optimize",
        description="Optimize the simulated model output",
        default=False
    )

    apply_modifs: BoolProperty(
        name="Apply Modifiers",
        description="Apply active viewport modifiers",
        default=True,
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
            self._actions.motion_name = action.name[:-(1 + len(obj.name))]
            break

        return super()._invoke(context, event)

    def draw(self, context):
        super().draw(context)
        layout = self.layout

        self.draw_panel_info(layout)
        self.draw_panel_general(layout)
        self.draw_panel_model(layout)

    def draw_panel_info(self, layout: bpy.types.UILayout):
        header, body = layout.panel(
            "SAIO_export_shapeanim_info", default_closed=False)
        header.label(text="Info")

        if body:
            body.label(text=f"Action to export: {self._actions.motion_name}")
            body.label(text="Using:")

            for obj, action in self._actions.actions.items():
                body.label(text=f"\"{action.name}\" for \"{obj.name}\"")

        return body

    def draw_panel_general(self, layout: bpy.types.UILayout):
        header, body = layout.panel(
            "SAIO_export_shapeanim_general", default_closed=True)
        header.label(text="General")

        if body:
            body.prop(self, "normal_mode")
            body.prop(self, "force_sort_bones")

        return body

    def draw_panel_model(self, layout: bpy.types.UILayout):
        header, body = layout.panel(
            "SAIO_export_shapeanim_model", default_closed=True)
        header.label(text="Model")

        if body:
            body.prop(self, "attach_format")
            body.prop(self, "optimize")
            body.prop(self, "apply_modifs")

        return body

    def export(self, context: bpy.types.Context):
        objects = {context.active_object}
        objects.update(context.active_object.children_recursive)

        model_eval = o_model.ModelEvaluator(
            context,
            self.attach_format,
            optimize=self.optimize,
            apply_modifs=self.apply_modifs,
            force_sort_bones=self.force_sort_bones)
        model_data = model_eval.evaluate(objects, self.attach_format == 'SA2')

        evaluator = o_shapemotion.ShapeMotionEvaluator(
            model_data,
            context,
            self.normal_mode)

        motion = evaluator.evaluate(self._actions)
        SA3D_Modeling.ANIMATION_FILE.WriteToFile(self.filepath, motion)
        return {'FINISHED'}
