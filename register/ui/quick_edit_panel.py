import bpy

from . import (
    viewport_toolbar,
    material_panel,
    land_entry_panel,
    node_panel,
    mesh_panel,
)

from .draw import (
    expand_menu
)

from ..property_groups import (
    quick_edit_properties
)

from ..operators import quick_edit_operators as qeo


class SAIO_PT_QuickEdit(viewport_toolbar.SAIO_PT_Viewport):
    bl_label = "Quick Edit"

    @staticmethod
    def draw_operators(layout: bpy.types.UILayout):

        # === Set props ===

        row = layout.row()
        row.alignment = 'CENTER'
        row.label(text="Apply Properties")
        row.scale_x = 1.0

        split = layout.split(factor=0.5)
        split.operator(
            qeo.SAIO_OT_QuickEdit_Set.bl_idname,
            text="Add Props").mode = 'ADD'

        split.operator(
            qeo.SAIO_OT_QuickEdit_Set.bl_idname,
            text="Remove props").mode = 'REMOVE'

        layout.operator(
            qeo.SAIO_OT_QuickEdit_Set.bl_idname,
            text="Apply All").mode = 'ALL'

        # === Selection ===

        outerBox = layout.box()

        row = outerBox.row()
        row.alignment = 'CENTER'
        row.label(text="Selection Tools")
        row.scale_x = 1.0

        row = outerBox.row()
        row.operator(
            qeo.SAIO_OT_QuickEdit_Select.bl_idname,
            text="Select").mode = 'ADD'

        row.operator(
            qeo.SAIO_OT_QuickEdit_Select.bl_idname,
            text="Clear").mode = 'REMOVE'

        row.operator(
            qeo.SAIO_OT_QuickEdit_Select.bl_idname,
            text="Invert").mode = 'INVERT'

        return outerBox

    @staticmethod
    def expand_select_menu(
            layout: bpy.types.UILayout,
            quick_edit: quick_edit_properties.SAIO_QuickEdit,
            selection_prop: str,
            panel_prop: str):

        row = layout.row()
        row.prop(quick_edit, selection_prop, text="")

        return expand_menu(
            row,
            quick_edit.panels,
            panel_prop)

    @staticmethod
    def draw_land_entry_selection(
            layout: bpy.types.UILayout,
            is_level: bool,
            quick_edit_properties: quick_edit_properties.SAIO_QuickEdit):

        box = layout.box()
        if not SAIO_PT_QuickEdit.expand_select_menu(
                box,
                quick_edit_properties,
                "use_land_entry_edit",
                "expanded_land_entry_quick_edit"):
            return

        land_entry_panel.SAIO_PT_LandEntry.draw_panel(
            box,
            is_level,
            quick_edit_properties.land_entry_properties,
            quick_edit_properties.panels,
            quick_edit_properties
        )

    @staticmethod
    def draw_node_selection(
            layout: bpy.types.UILayout,
            quick_edit_properties: quick_edit_properties.SAIO_QuickEdit):

        box = layout.box()
        if not SAIO_PT_QuickEdit.expand_select_menu(
                box,
                quick_edit_properties,
                "use_node_edit",
                "expanded_node_quick_edit"):
            return

        node_panel.SAIO_PT_Node.draw_node_properties(
            box,
            quick_edit_properties.node_properties
        )

    @staticmethod
    def draw_mesh_selection(
            layout: bpy.types.UILayout,
            quick_edit_properties: quick_edit_properties.SAIO_QuickEdit):

        box = layout.box()
        if not SAIO_PT_QuickEdit.expand_select_menu(
                box,
                quick_edit_properties,
                "use_mesh_edit",
                "expanded_mesh_quick_edit"):
            return

        mesh_panel.SAIO_PT_Mesh.draw_mesh_properties(
            box,
            quick_edit_properties.mesh_properties
        )

    @staticmethod
    def draw_material_selection(
            layout: bpy.types.UILayout,
            quick_edit_properties: quick_edit_properties.SAIO_QuickEdit):

        box = layout.box()
        if not SAIO_PT_QuickEdit.expand_select_menu(
                box,
                quick_edit_properties,
                "use_material_edit",
                "expanded_material_quick_edit"):
            return

        material_panel.SAIO_PT_Material.draw_panel(
            box,
            None,
            quick_edit_properties.material_properties,
            quick_edit_properties.panels,
            quick_edit_properties,
            False
        )

    def draw(self, context):

        if context.mode not in ['OBJECT', 'POSE', 'EDIT_ARMATURE']:
            self.layout.box().label(
                text=f"Not supported in {context.mode} mode")
            return

        box = SAIO_PT_QuickEdit.draw_operators(self.layout)

        quick_edit_properties = context.scene.saio_settings.quick_edit

        SAIO_PT_QuickEdit.draw_node_selection(
            box,
            quick_edit_properties
        )

        if context.mode == 'OBJECT':

            SAIO_PT_QuickEdit.draw_land_entry_selection(
                box,
                context.scene.saio_settings.scene_is_level,
                quick_edit_properties
            )

            SAIO_PT_QuickEdit.draw_mesh_selection(
                box,
                quick_edit_properties
            )

            SAIO_PT_QuickEdit.draw_material_selection(
                box,
                quick_edit_properties
            )
