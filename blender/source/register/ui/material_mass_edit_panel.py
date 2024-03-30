import bpy

from . import (
    material_panel,
    viewport_toolbar,
)

from ..operators import material_mass_edit_operators as mmeo


class SAIO_PT_MaterialMassEdit(viewport_toolbar.ViewportToolPanel):
    bl_label = "Material Mass Edit"

    @staticmethod
    def draw_operators(layout: bpy.types.UILayout):

        split = layout.split(factor=0.5)
        split.operator(
            mmeo.SAIO_OT_MaterialMassEdit_Set.bl_idname,
            text="Add Props").mode = 'ADD'

        split.operator(
            mmeo.SAIO_OT_MaterialMassEdit_Set.bl_idname,
            text="Remove props").mode = 'REMOVE'

        layout.operator(
            mmeo.SAIO_OT_MaterialMassEdit_Set.bl_idname,
            text="Apply All").mode = 'ALL'

        layout.operator(
            mmeo.SAIO_OT_MaterialMassEdit_Reset.bl_idname)

    def draw(self, context):

        if context.mode != 'OBJECT':
            self.layout.box().label(
                text=f"Not supported in {context.mode} mode")
            return

        SAIO_PT_MaterialMassEdit.draw_operators(self.layout)

        mass_edit_properties = context.scene.saio_scene.material_mass_edit

        material_panel.SAIO_PT_Material.draw_material_properties(
            self.layout.box(),
            None,
            mass_edit_properties.material_properties,
            mass_edit_properties,
            False,
            False)
