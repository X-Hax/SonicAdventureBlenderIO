import bpy

from .base_panel import PropertiesPanel

from ..property_groups.scene_properties import SAIO_Scene
from ..property_groups.event_entry_properties import SAIO_EventEntry

from ...utility.draw import prop_advanced

ATTRIBUTE_LIST = [
    "layer",
    "blare",
    "reflection",
    "unk0",
    "unk2",
    "unk4",
    "unk5",
    "unk6",
    "unk9",
]


class SAIO_PT_EventEntry(PropertiesPanel):
    bl_label = "SAIO Event Entry Properties"
    bl_context = "object"

    @staticmethod
    def draw_event_entry_properties(
            layout: bpy.types.UILayout,
            event_entry_properties: SAIO_EventEntry):

        prop_advanced(
            layout,
            "Entry Type: ",
            event_entry_properties,
            "entry_type")

        if event_entry_properties.entry_type in ['CHUNK', 'GC']:
            layout.prop_search(
                event_entry_properties, "shadow_model", bpy.data, "objects")

            for attribute in ATTRIBUTE_LIST:
                layout.prop(event_entry_properties, attribute)

            layout.separator()
            layout.label(text="Root scene attributes")
            layout.prop(event_entry_properties, "enable_lighting")
            layout.prop(event_entry_properties, "disable_shadow_catching")

    # === Overridden methods === #

    @classmethod
    def verify(cls, context: bpy.types.Context):
        error = SAIO_Scene.check_is_event(context)
        if error is not None:
            return error

        if context.active_object is None:
            return "No active object"

        error = SAIO_EventEntry.check_is_event_entry(context.active_object)
        if error is not None:
            return error

        return None

    def draw_panel(self, context: bpy.types.Context):
        SAIO_PT_EventEntry.draw_event_entry_properties(
            self.layout,
            context.active_object.saio_event_entry)
