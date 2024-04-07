import bpy

from .base_panel import PropertiesPanel
from .event_uv_anim_panel import draw_event_uv_anim_list

from ..property_groups.scene_properties import SAIO_Scene
from ..property_groups.event_properties import SAIO_Event
from ..property_groups.panel_properties import SAIO_PanelSettings
from ..operators import event_operators as eveop

EVENTLIST_TOOLS = [
    (
        eveop.SAIO_OT_EventScene_Add.bl_idname,
        "ADD",
        {}
    ),
    (
        eveop.SAIO_OT_EventScene_Remove.bl_idname,
        "REMOVE",
        {}
    ),
    None,
    (
        eveop.SAIO_OT_EventScene_Move.bl_idname,
        "TRIA_UP",
        {"direction": "UP"}
    ),
    (
        eveop.SAIO_OT_EventScene_Move.bl_idname,
        "TRIA_DOWN",
        {"direction": "DOWN"}
    )
]


class SAIO_UL_EventSceneList(bpy.types.UIList):

    def draw_item( # pylint: disable=signature-differs
            self,
            context: bpy.types.Context,
            layout: bpy.types.UILayout,
            data,
            item,
            icon: str,
            active_data,
            active_property,
            index,
            flt_flag):

        split = layout.split(factor=0.4)

        split.label(
            text=str(index + 1),
            icon='X' if item.scene is None else 'CHECKMARK')

        split.prop(
            item,
            "name",
            text="",
            emboss=False)


class SAIO_MT_EventSceneContextMenu(bpy.types.Menu):
    bl_label = "Event scene list operations"

    def draw(self, context):
        layout = self.layout

        layout.operator(eveop.SAIO_OT_EventScene_Clear.bl_idname)


class SAIO_PT_Event(PropertiesPanel):
    bl_label = "SAIO Event"
    bl_context = "scene"

    @staticmethod
    def draw_eventscene_list(
            layout: bpy.types.UILayout,
            event_list: SAIO_Event):

        layout.label(text="Event Scenes:")

        row = layout.row()
        row.template_list(
            "SAIO_UL_EventSceneList",
            "",
            event_list,
            "elements",
            event_list,
            "active_index")

        column = row.column()

        for tool in EVENTLIST_TOOLS:
            if tool is None:
                column.separator()
                continue

            operator = column.operator(
                tool[0],
                icon=tool[1],
                text="")

            for k, v in tool[2].items():
                setattr(operator, k, v)

        column.menu(
            "SAIO_MT_EventSceneContextMenu",
            icon='DOWNARROW_HLT',
            text="")

        if event_list.active_index >= 0:
            eventscene = event_list[
                event_list.active_index]

            layout.prop(eventscene, "name")
            layout.prop_search(eventscene, "scene", bpy.data, "scenes")

    @staticmethod
    def draw_object_bone(
            layout: bpy.types.UILayout,
            properties,
            name: str):

        layout.prop_search(
            properties,
            name,
            bpy.data,
            "objects"
        )

        obj = getattr(properties, name)
        if obj is not None and obj.type == "ARMATURE":
            layout.prop_search(
                properties,
                name + "_bone",
                obj.data,
                "bones"
            )

    @staticmethod
    def draw_override_upgrade_menu(
            layout: bpy.types.UILayout,
            event_properties: SAIO_Event,
            panel_properties: SAIO_PanelSettings):

        layout.prop(panel_properties, "override_upgrade_menu")

        upgrade_properties = getattr(
            event_properties,
            "ou_" + panel_properties.override_upgrade_menu.lower()
        )

        SAIO_PT_Event.draw_object_bone(
            layout, upgrade_properties, "base")

        SAIO_PT_Event.draw_object_bone(
            layout, upgrade_properties, "override1")

        SAIO_PT_Event.draw_object_bone(
            layout, upgrade_properties, "override2")

    @staticmethod
    def draw_attach_upgrade_menu(
            layout: bpy.types.UILayout,
            event_properties: SAIO_Event,
            panel_properties: SAIO_PanelSettings):

        layout.prop(panel_properties, "attach_upgrade_menu")

        upgrade_properties = getattr(
            event_properties,
            "au_" + panel_properties.attach_upgrade_menu.lower()
        )

        layout.prop_search(
            upgrade_properties,
            "model1",
            bpy.data,
            "objects"
        )

        SAIO_PT_Event.draw_object_bone(
            layout, upgrade_properties, "target1")

        layout.prop_search(
            upgrade_properties,
            "model2",
            bpy.data,
            "objects"
        )

        SAIO_PT_Event.draw_object_bone(
            layout, upgrade_properties, "target2")

    @staticmethod
    def draw_event_properties(
            layout: bpy.types.UILayout,
            event_properties: SAIO_Event,
            panel_properties: SAIO_PanelSettings):

        SAIO_PT_Event.draw_eventscene_list(
            layout, event_properties)

        layout.prop(event_properties, "drop_shadow_control")

        box = layout.box()

        SAIO_PT_Event.draw_object_bone(
            box, event_properties, "tails_tails")

        header, box = layout.panel("saio_scene_override_upgrades", default_closed=True)
        header.label(text="Integrated Upgrades")
        if box:
            SAIO_PT_Event.draw_override_upgrade_menu(
                box,
                event_properties,
                panel_properties)

        header, box = layout.panel("saio_scene_attach_upgrades", default_closed=True)
        header.label(text="Overlay Upgrades")
        if box:
            SAIO_PT_Event.draw_attach_upgrade_menu(
                box,
                event_properties,
                panel_properties)

        header, box = layout.panel("saio_scene_tex_anim", default_closed=True)
        header.label(text="Texture animations")
        if box:
            draw_event_uv_anim_list(box, event_properties.uv_animations)

    # === Overriden methods ===

    @classmethod
    def verify(cls, context: bpy.types.Context):
        return SAIO_Scene.check_is_event_root(context)

    def draw_panel(self, context):

        SAIO_PT_Event.draw_event_properties(
            self.layout,
            context.scene.saio_scene.event,
            context.scene.saio_scene.panels)
