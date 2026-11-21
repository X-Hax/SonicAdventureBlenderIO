import bpy

from ..operators.material_operators import (
    SAIO_OT_Material_UpdateProperties,
    SAIO_OT_Material_UpdateTextures,
    SAIO_OT_Material_AttemptConvert,
    SAIO_OT_Material_AssembleTextureList
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


class SAIO_PT_VTP_Material(ViewportToolPanel):
    bl_label = "Material"

    def draw(self, context):

        layout = self.layout
        layout.operator(SAIO_OT_Material_UpdateProperties.bl_idname)
        layout.operator(SAIO_OT_Material_UpdateTextures.bl_idname)
        layout.operator(SAIO_OT_Material_AttemptConvert.bl_idname)
        layout.operator(SAIO_OT_Material_AssembleTextureList.bl_idname)

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
