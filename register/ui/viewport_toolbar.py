import bpy

from . import (
    scene_panel,
    landtable_panel,
    land_entry_panel,
    node_panel,
    mesh_panel,
    material_panel,
)

from ..operators import (
    SAIO_OT_Material_TextureFromID,
    SAIO_OT_Material_TextureToID,
    SAIO_OT_Material_UpdateNodes,

    SAIO_OT_Import_Model,
    SAIO_OT_Import_Level,

    SAIO_OT_Export_SA1MDL,
    SAIO_OT_Export_SA2MDL,
    SAIO_OT_Export_SA2BMDL,
    SAIO_OT_Export_SA1LVL,
    SAIO_OT_Export_SA2LVL,
    SAIO_OT_Export_SA2BLVL,
)

from ...utils import (
    is_landtable,
    is_land_entry,
    get_active_node_properties
)


class SAIO_PT_Viewport(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SA I/O"
    bl_options = {"DEFAULT_CLOSED"}


class SAIO_PT_VPTools(SAIO_PT_Viewport):
    bl_label = "Tools"

    def draw(self, context):

        layout = self.layout

        layout.operator(
            SAIO_OT_Import_Model.bl_idname,
            text="Import Model")

        layout.operator(
            SAIO_OT_Import_Level.bl_idname,
            text="Import Level")
        layout.separator()

        if context.scene.saio_scene.scene_is_level:

            layout.operator(
                SAIO_OT_Export_SA1LVL.bl_idname,
                text="Export SA1LVL")

            layout.operator(
                SAIO_OT_Export_SA2LVL.bl_idname,
                text="Export SA2LVL")

            layout.operator(
                SAIO_OT_Export_SA2BLVL.bl_idname,
                text="Export SA2LVL")

        else:

            layout.operator(
                SAIO_OT_Export_SA1MDL.bl_idname,
                text="Export SA1MDL")

            layout.operator(
                SAIO_OT_Export_SA2MDL.bl_idname,
                text="Export SA2MDL")

            layout.operator(
                SAIO_OT_Export_SA2BMDL.bl_idname,
                text="Export SA2BMDL")

        layout.separator()
        layout.operator(SAIO_OT_Material_TextureFromID.bl_idname)
        layout.operator(SAIO_OT_Material_TextureToID.bl_idname)
        layout.operator(SAIO_OT_Material_UpdateNodes.bl_idname)


class SAIO_PT_VPSettings(SAIO_PT_Viewport):
    bl_label = "Settings"

    def draw(self, context):
        scene_panel.SAIO_PT_Scene.draw_panel(
            self.layout,
            context.scene,
            context.scene.saio_scene.viewport_panels
        )


class SAIO_PT_VPLandTable(SAIO_PT_Viewport):
    bl_label = "Landtable"

    def draw(self, context):

        if not is_landtable(context):
            self.layout.box().label(text="Scene is not marked as a level")
            return

        landtable_panel.SAIO_PT_Landtable.draw_panel(
            self.layout,
            context.scene.saio_scene.landtable
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
            context.scene.saio_scene.viewport_panels
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

        slot = None
        if object.active_material_index < len(object.material_slots):
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
            material_panel.SAIO_PT_Material.draw_panel(
                self.layout,
                obj.active_material,
                obj.active_material.saio_material,
                context.scene.saio_scene.viewport_panels
            )
