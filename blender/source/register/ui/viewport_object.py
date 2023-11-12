import bpy

from . import (
    land_entry_panel,
    node_panel,
    mesh_panel,
    material_panel,
    texture_panel,
    texturename_panel,
    event_entry_panel,
    event_node_uv_anim_panel
)


class ViewportObjectPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SAIO Object"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_target_header(self, context: bpy.types.Context): # pylint: disable=unused-argument
        return

    def get_target_name(self, context: bpy.types.Context):
        return f"Active Object: {context.active_object.name}"

    @classmethod
    def verify(cls, context):
        return cls.base.verify(context) # pylint: disable=no-member

    def draw(self, context):
        self.draw_target_header(context)
        return self.base.draw(self, context) # pylint: disable=no-member

    def draw_panel(self, context):
        self.layout.label(text=self.get_target_name(context))
        return self.base.draw_panel(self, context) # pylint: disable=no-member


class SAIO_PT_VOP_LandEntry(ViewportObjectPanel):
    bl_label = "Land Entry"
    base = land_entry_panel.SAIO_PT_LandEntry


class SAIO_PT_VOP_EventEntry(ViewportObjectPanel):
    bl_label = "Event Entry"
    base = event_entry_panel.SAIO_PT_EventEntry


class SAIO_PT_VOP_EventNodeUVAnim(ViewportObjectPanel):
    bl_label = "Event Node UV Animations"
    base = event_node_uv_anim_panel.SAIO_PT_EventNodeUVAnimPanel


class SAIO_PT_VOP_Node(ViewportObjectPanel):
    bl_label = "Node"

    def draw(self, context):
        from ..property_groups.node_properties import SAIO_Node

        properties = SAIO_Node.get_active_node_properties(context)

        if properties is None:
            self.layout.box().label(text="Active object is not a Node")
            return

        object_type = "Object" if context.active_object.mode == "OBJECT" else "Bone"
        self.layout.label(text=f"Active {object_type}: {properties[0]}")

        node_panel.SAIO_PT_Node.draw_node_properties(
            self.layout, properties[1])


class SAIO_PT_VOP_Textures(ViewportObjectPanel):
    bl_label = "Textures"
    base = texture_panel.SAIO_PT_ObjectTextures


class SAIO_PT_VOP_Texturenames(ViewportObjectPanel):
    bl_label = "Texture Names"
    base = texturename_panel.SAIO_PT_ObjectTexturenames


class SAIO_PT_VPMesh(ViewportObjectPanel):
    bl_label = "Mesh"
    base = mesh_panel.SAIO_PT_Mesh

    def get_target_name(self, context: bpy.types.Context):
        return f"Active Mesh: {context.active_object.data.name}"


class SAIO_PT_VPMaterial(ViewportObjectPanel):
    bl_label = "Material"
    base = material_panel.SAIO_PT_Material

    @staticmethod
    def draw_material_list(
            layout: bpy.types.UILayout,
            obj: bpy.types.Object):

        is_sortable = len(obj.material_slots) > 1
        rows = 3
        if is_sortable:
            rows = 5

        row = layout.row()

        row.template_list(
            "MATERIAL_UL_matslots",
            "",
            obj,
            "material_slots",
            obj,
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
        row.template_ID(obj, "active_material", new="material.new")

        slot = None
        if obj.active_material_index < len(obj.material_slots):
            slot = obj.material_slots[obj.active_material_index]

        if slot:
            icon_link = 'MESH_DATA' if slot.link == 'DATA' else 'OBJECT_DATA'
            row.prop(slot, "link", icon=icon_link, icon_only=True)

        if obj.mode == 'EDIT':
            row = layout.row(align=True)
            row.operator("object.material_slot_assign", text="Assign")
            row.operator("object.material_slot_select", text="Select")
            row.operator("object.material_slot_deselect", text="Deselect")

    def draw_target_header(self, context: bpy.types.Context):
        if (context.active_object is not None
                and context.active_object.type == 'MESH'):

            SAIO_PT_VPMaterial.draw_material_list(
                self.layout,
                context.active_object)

    def get_target_name(self, context: bpy.types.Context):
        return f"Active Material: {context.active_object.active_material.name}"
