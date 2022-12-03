import bpy

from .draw import (
    prop_advanced,
    expand_menu
)

from ..property_groups import (
    land_entry_properties,
    panel_properties,
    quick_edit_properties
)

from ...utils import is_land_entry


ATTRIBUTE_LISTS = {
    "UNIVERSAL": [
        "sf_visible",
        "sf_solid",
        "sf_water",
        "sf_water_no_alpha",
        None,
        "sf_accelerate",
        "sf_low_acceleration",
        "sf_no_acceleration",
        "sf_increased_acceleration",
        "sf_tube_acceleration",
        None,
        "sf_no_friction",
        "sf_cannot_land",
        "sf_unclimbable",
        "sf_stairs",
        "sf_diggable",
        "sf_hurt",
        "sf_dynamic_collision",
        "sf_water_collision",
        None,
        "sf_gravity",
        None,
        "sf_footprints",
        "sf_no_shadows",
        "sf_no_fog",
        "sf_low_depth",
        "sf_use_sky_draw_distance",
        "sf_easy_draw",
        "sf_no_zwrite",
        "sf_draw_by_nesh",
        "sf_enable_manipulation",
        "sf_waterfall",
        "sf_chaos0_land",
        None,
        "sf_transform_bounds",
        "sf_bounds_radius_small",
        "sf_bounds_radius_tiny",
        None,
        "sf_sa1_unknown9",
        "sf_sa1_unknown11",
        "sf_sa1_unknown15",
        "sf_sa1_unknown19",
        None,
        "sf_sa2_unknown6",
        "sf_sa2_unknown9",
        "sf_sa2_unknown14",
        "sf_sa2_unknown16",
        "sf_sa2_unknown17",
        "sf_sa2_unknown18",
        "sf_sa2_unknown25",
        "sf_sa2_unknown26",
    ],
    "SA1": [
        "sf_solid",
        "sf_water",
        "sf_no_friction",
        "sf_no_acceleration",
        None,
        "sf_low_acceleration",
        "sf_use_sky_draw_distance",
        "sf_cannot_land",
        "sf_increased_acceleration",
        None,
        "sf_diggable",
        "sf_sa1_unknown9",
        "sf_waterfall",
        "sf_sa1_unknown11",
        None,
        "sf_unclimbable",
        "sf_chaos0_land",
        "sf_stairs",
        "sf_sa1_unknown15",
        None,
        "sf_hurt",
        "sf_tube_acceleration",
        "sf_low_depth",
        "sf_sa1_unknown19",
        None,
        "sf_footprints",
        "sf_accelerate",
        "sf_water_collision",
        "sf_gravity",
        None,
        "sf_no_zwrite",
        "sf_draw_by_nesh",
        "sf_enable_manipulation",
        "sf_dynamic_collision",
        None,
        "sf_transform_bounds",
        "sf_bounds_radius_small",
        "sf_bounds_radius_tiny",
        "sf_visible"
    ],
    "SA2": [
        "sf_solid",
        "sf_water",
        "sf_no_friction",
        "sf_no_acceleration",
        None,
        "sf_low_acceleration",
        "sf_diggable",
        "sf_sa2_unknown6",
        "sf_unclimbable",
        None,
        "sf_stairs",
        "sf_sa2_unknown9",
        "sf_hurt",
        "sf_footprints",
        None,
        "sf_cannot_land",
        "sf_water_no_alpha",
        "sf_sa2_unknown14",
        "sf_no_shadows",
        None,
        "sf_sa2_unknown16",
        "sf_sa2_unknown17",
        "sf_sa2_unknown18",
        "sf_gravity",
        None,
        "sf_tube_acceleration",
        "sf_increased_acceleration",
        "sf_no_fog",
        "sf_use_sky_draw_distance",
        None,
        "sf_easy_draw",
        "sf_sa2_unknown25",
        "sf_sa2_unknown26",
        "sf_dynamic_collision",
        None,
        "sf_transform_bounds",
        "sf_bounds_radius_small",
        "sf_bounds_radius_tiny",
        "sf_visible",
    ],
}


class SAIO_PT_LandEntry(bpy.types.Panel):
    bl_label = "SAIO Land Entry Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_options = {"DEFAULT_CLOSED"}

    @staticmethod
    def draw_attributes(
            layout: bpy.types.UILayout,
            land_entry_properties: land_entry_properties.SAIO_LandEntry,
            panel_settings: panel_properties.SAIO_PanelSettings):

        box = layout.box()
        if not expand_menu(box, panel_settings, "expanded_surface_attributes"):
            return

        attribute_list = ATTRIBUTE_LISTS[
            panel_settings.land_entry_surface_attributes_editmode]

        for attribute in attribute_list:
            if attribute is None:
                box.separator(factor=2)
            else:
                box.prop(land_entry_properties, attribute)

    @staticmethod
    def draw_panel(
            layout: bpy.types.UILayout,
            is_level: bool,
            land_entry_properties: land_entry_properties.SAIO_LandEntry,
            panel_settings: panel_properties.SAIO_PanelSettings,
            quick_edit_properties: quick_edit_properties.SAIO_QuickEdit = None):

        if not is_level:
            layout.box().label(text="Scene is not marked as a level")
            return

        prop_advanced(
            layout,
            "Blockit (hex):  0x",
            land_entry_properties,
            "blockbit",
            quick_edit_properties,
            "apply_blockbit")

        layout.separator(factor=1)

        prop_advanced(
            layout,
            "Surface attributes edit mode",
            panel_settings,
            "land_entry_surface_attributes_editmode")

        SAIO_PT_LandEntry.draw_attributes(
            layout,
            land_entry_properties,
            panel_settings)

    @classmethod
    def poll(cls, context):
        return is_land_entry(context)

    def draw(self, context):

        SAIO_PT_LandEntry.draw_panel(
            self.layout,
            context.scene.saio_settings.scene_is_level,
            context.active_object.saio_land_entry,
            context.scene.saio_settings.panels
        )
