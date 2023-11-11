import bpy

from ..operators.material_operators import (
    SAIO_OT_Material_UpdateProperties,
    SAIO_OT_Material_UpdateTextures,
    SAIO_OT_Material_AttemptConvert,
    SAIO_OT_Material_AssembleTextureList
)

from ..operators.import_operators import (
    SAIO_OT_Import_Model,
    SAIO_OT_Import_Landtable,
    SAIO_OT_Import_Event
)

from ..operators.anim_import_operators import (
    SAIO_OT_Import_Node_Animation,
    SAIO_OT_Import_Camera_Animation,
    SAIO_OT_Import_Shape_Animation
)

from ..operators.export_operators import (
    SAIO_OT_Export_SA1MDL,
    SAIO_OT_Export_SA2MDL,
    SAIO_OT_Export_SA2BMDL,
    SAIO_OT_Export_SA1LVL,
    SAIO_OT_Export_SA2LVL,
    SAIO_OT_Export_SA2BLVL,
    SAIO_OT_Export_Event
)

from ..operators.anim_export_operators import (
    SAIO_OT_Export_Node_Animation,
    SAIO_OT_Export_Node_Animations,
    SAIO_OT_Export_Shape_Animation,
    SAIO_OT_Export_Camera_Animation
)

from ..operators.tool_operators import (
    SAIO_OT_AutoNodeAttributes,
    SAIO_OT_TestBakeAnimation,
    SAIO_OT_ArmatureFromObjects,
    SAIO_OT_ArmaturCorrectVisual,
    SAIO_OT_SetupCamera,
    SAIO_OT_CopyVertexIndicesToClipboard,
)

from ..operators.path_operators import (
    SAIO_OT_Import_Path,
    SAIO_OT_Path_Generate,
    SAIO_OT_Export_Path
)

from ..operators.migration_operators import (
    SAIO_OT_MigrateCheck,
    SAIO_OT_MigrateData,
    SAIO_OT_MigrateArmature,
    SAIO_OT_MigratePath
)

from ..operators.info_operators import (
    SAIO_OT_Info_Manual,
    SAIO_OT_Info_Discord
)


class ViewportToolPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SAIO Tools"
    bl_options = {'DEFAULT_CLOSED'}


class SAIO_PT_VTP_Import(ViewportToolPanel):
    bl_label = "Import"

    def draw(self, context):

        layout = self.layout

        layout.operator(
            SAIO_OT_Import_Model.bl_idname,
            text="Import Model")

        layout.operator(
            SAIO_OT_Import_Landtable.bl_idname,
            text="Import Landtable")

        layout.operator(
            SAIO_OT_Import_Event.bl_idname,
            text="Import SA2 Event")
        layout.separator()

        layout.separator()

        layout.operator(SAIO_OT_Import_Path.bl_idname)
        layout.operator(SAIO_OT_Import_Node_Animation.bl_idname)
        layout.operator(SAIO_OT_Import_Shape_Animation.bl_idname)
        layout.operator(SAIO_OT_Import_Camera_Animation.bl_idname)


class SAIO_PT_VTP_Export(ViewportToolPanel):
    bl_label = "Export"

    def draw(self, context):
        layout = self.layout

        if context.scene.saio_scene.scene_type == "LVL":

            layout.operator(
                SAIO_OT_Export_SA1LVL.bl_idname,
                text="Export SA1LVL")

            layout.operator(
                SAIO_OT_Export_SA2LVL.bl_idname,
                text="Export SA2LVL")

            layout.operator(
                SAIO_OT_Export_SA2BLVL.bl_idname,
                text="Export SA2BLVL")

        elif context.scene.saio_scene.scene_type == 'MDL':

            layout.operator(
                SAIO_OT_Export_SA1MDL.bl_idname,
                text="Export SA1MDL")

            layout.operator(
                SAIO_OT_Export_SA2MDL.bl_idname,
                text="Export SA2MDL")

            layout.operator(
                SAIO_OT_Export_SA2BMDL.bl_idname,
                text="Export SA2BMDL")

        elif context.scene.saio_scene.scene_type in {'EVR', 'EVC'}:
            layout.operator(
                SAIO_OT_Export_Event.bl_idname,
                text="Export SA2 Event")

        layout.separator()
        layout.operator(SAIO_OT_Export_Path.bl_idname)
        layout.operator(SAIO_OT_Export_Node_Animation.bl_idname)
        layout.operator(SAIO_OT_Export_Node_Animations.bl_idname)
        layout.operator(SAIO_OT_Export_Shape_Animation.bl_idname)
        layout.operator(SAIO_OT_Export_Camera_Animation.bl_idname)


class SAIO_PT_VTP_Material(ViewportToolPanel):
    bl_label = "Material"

    def draw(self, context):

        layout = self.layout
        layout.operator(SAIO_OT_Material_UpdateProperties.bl_idname)
        layout.operator(SAIO_OT_Material_UpdateTextures.bl_idname)
        layout.operator(SAIO_OT_Material_AttemptConvert.bl_idname)
        layout.operator(SAIO_OT_Material_AssembleTextureList.bl_idname)


class SAIO_PT_VTP_Utilities(ViewportToolPanel):
    bl_label = "Utilities"

    def draw(self, context):

        layout = self.layout

        layout.operator(SAIO_OT_AutoNodeAttributes.bl_idname)
        layout.operator(SAIO_OT_ArmatureFromObjects.bl_idname)
        layout.operator(SAIO_OT_ArmaturCorrectVisual.bl_idname)

        layout.separator()

        layout.operator(SAIO_OT_Path_Generate.bl_idname)
        layout.operator(SAIO_OT_SetupCamera.bl_idname)
        layout.operator(SAIO_OT_CopyVertexIndicesToClipboard.bl_idname)
        layout.operator(SAIO_OT_TestBakeAnimation.bl_idname)


class SAIO_PT_VTP_Migration(bpy.types.Panel):
    bl_label = "Migration"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SAIO Tools"

    def draw(self, context):
        from ...migration import migration_checks

        layout = self.layout
        saio = context.scene.saio_scene

        if migration_checks.is_old_addon_enabled(context):
            box = layout.box()
            box.label(text="!! WARNING !!")
            box.label(text="You appear to have the old addon enabled!")
            box.label(text="Please make sure that it's disabled!")
            box.label(text="It's best to uninstall altogether.")

        layout.operator(SAIO_OT_MigrateCheck.bl_idname)
        if not saio.checked_for_migrate_data:
            box = layout.box()
            box.label(text="Not yet checked for migrate data!")
            return

        if not saio.found_migrate_data:
            box = layout.box()
            box.label(text="Nothing to migrate")
            return

        layout.operator(SAIO_OT_MigrateData.bl_idname)
        layout.operator(SAIO_OT_MigrateArmature.bl_idname)
        layout.operator(SAIO_OT_MigratePath.bl_idname)


class SAIO_PT_VTP_Info(bpy.types.Panel):
    bl_label = "Info"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SAIO Tools"

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="You can right click any button")
        box.label(text="or property field added by the")
        box.label(text="addon and click \"Online Manual\"")
        box.label(text="to read about it.")

        layout.operator(SAIO_OT_Info_Manual.bl_idname)
        layout.operator(SAIO_OT_Info_Discord.bl_idname)
