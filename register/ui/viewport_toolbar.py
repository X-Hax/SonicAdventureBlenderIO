import bpy

from ...utils import (
    is_landtable,
    is_land_entry,
    get_active_node_properties
)

from . import (
    settings_panel,
    landtable_panel,
    land_entry_panel,
    node_panel,
    mesh_panel,
    material_panel,
)


class SAIO_PT_Viewport(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SA I/O"
    bl_options = {"DEFAULT_CLOSED"}


class SAIO_PT_VPSettings(SAIO_PT_Viewport):
    bl_label = "Settings"

    def draw(self, context):
        settings_panel.SAIO_PT_Settings.draw_panel(
            self.layout,
            context.scene,
            context.scene.saio_settings.viewport_panels
        )


class SAIO_PT_VPLandTable(SAIO_PT_Viewport):
    bl_label = "Landtable"

    def draw(self, context):

        if not is_landtable(context):
            self.layout.box().label(text="Scene is not marked as a level")
            return

        landtable_panel.SAIO_PT_Landtable.draw_panel(
            self.layout,
            context.scene.saio_settings.landtable
        )


class SAIO_PT_VPLandEntry(SAIO_PT_Viewport):
    bl_label = "Land Entry"

    def draw(self, context):

        if not is_landtable(context):
            self.layout.box().label(text="Scene is not marked as a level")
            return

        if not is_land_entry(context):
            self.layout.box().label(text="Active object is not a Land entry")
            return

        self.layout.label(
            text=f"Selected object: {context.active_object.name}"
        )

        land_entry_panel.SAIO_PT_LandEntry.draw_panel(
            self.layout,
            context.active_object.saio_land_entry,
            context.scene.saio_settings.viewport_panels
        )


class SAIO_PT_VPNode(SAIO_PT_Viewport):
    bl_label = "Node"

    def draw(self, context):

        properties = get_active_node_properties(context)

        if properties is None:
            self.layout.box().label(text="Active selection is not a Node")
            return

        type = "Object" if context.active_object.mode == "OBJECT" else "Bone"
        self.layout.label(text=f"Selected {type}: {properties[0]}")

        node_panel.SAIO_PT_Node.draw_node_properties(
            self.layout,
            properties[1]
        )


class SAIO_PT_VPMesh(SAIO_PT_Viewport):
    bl_label = "Mesh"

    def draw(self, context):

        obj = context.active_object
        if obj is None or obj.type != 'MESH':
            self.layout.box().label(text="Active selection has no Mesh")
            return

        self.layout.label(text=f"Selected Mesh: {obj.data.name}")

        mesh_panel.SAIO_PT_Mesh.draw_mesh_properties(
            self.layout,
            obj.data.saio_mesh
        )


class SAIO_PT_VPMaterial(SAIO_PT_Viewport):
    bl_label = "Material"

    def draw_material_list(
            layout: bpy.types.UILayout,
            object: bpy.types.Object):

        is_sortable = len(object.material_slots) > 1
        rows = 3
        if is_sortable:
            rows = 5

        row = layout.row()

        row.template_list(
            "MATERIAL_UL_matslots",
            "",
            object,
            "material_slots",
            object,
            "active_material_index",
            rows=rows)

        col = row.column(align=True)
        col.operator("object.material_slot_add", icon='ADD', text="")
        col.operator("object.material_slot_remove", icon='REMOVE', text="")

        col.separator()

        col.menu("MATERIAL_MT_context_menu", icon='DOWNARROW_HLT', text="")

        if is_sortable:
            col.separator()

            col.operator(
                "object.material_slot_move",
                icon='TRIA_UP',
                text="").direction = 'UP'

            col.operator(
                "object.material_slot_move",
                icon='TRIA_DOWN',
                text="").direction = 'DOWN'

        row = layout.row()
        row.template_ID(object, "active_material", new="material.new")

        slot = object.material_slots[object.active_material_index]
        if slot:
            icon_link = 'MESH_DATA' if slot.link == 'DATA' else 'OBJECT_DATA'
            row.prop(slot, "link", icon=icon_link, icon_only=True)

        if object.mode == 'EDIT':
            row = layout.row(align=True)
            row.operator("object.material_slot_assign", text="Assign")
            row.operator("object.material_slot_select", text="Select")
            row.operator("object.material_slot_deselect", text="Deselect")

    def draw(self, context):

        obj = context.active_object
        if obj is None or obj.type != 'MESH':
            self.layout.box().label(text="Active selection has no Materials")
            return

        SAIO_PT_VPMaterial.draw_material_list(self.layout, obj)

        if obj.active_material is not None:
            material_panel.SAIO_PT_Material.draw_material_properties(
                self.layout,
                obj.active_material,
                context.scene.saio_settings.viewport_panels
            )
