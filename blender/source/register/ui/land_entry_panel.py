import bpy

from .base_panel import PropertiesPanel

from ..property_groups.scene_properties import SAIO_Scene
from ..property_groups.land_entry_properties import SAIO_LandEntry
from ..property_groups.panel_properties import SAIO_PanelSettings

from ...utility.draw import prop_advanced


LAND_ENTRY_ATTRIBUTE_LISTS = {
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
        "sf_draw_by_mesh",
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
        "sf_draw_by_mesh",
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


class SAIO_PT_LandEntry(PropertiesPanel):
    bl_label = "SAIO Land Entry Properties"
    bl_context = "object"

    @staticmethod
    def draw_attributes(
            layout: bpy.types.UILayout,
            land_entry_properties: SAIO_LandEntry,
            panel_settings: SAIO_PanelSettings,
            draw_unknown: bool):

        header, box = layout.panel("saio_obj_surface", default_closed=True)
        header.label(text="Surface attributes")
        if not box:
            return

        attribute_list = LAND_ENTRY_ATTRIBUTE_LISTS[
            panel_settings.land_entry_surface_attributes_editmode]

        for attribute in attribute_list:
            if attribute is None:
                box.separator(factor=2)
            elif not draw_unknown and "unknown" in attribute:
                continue
            else:
                box.prop(land_entry_properties, attribute)

    @staticmethod
    def draw_static_properties(
            layout: bpy.types.UILayout,
            land_entry_properties: SAIO_LandEntry,
            panel_settings: SAIO_PanelSettings):

        prop_advanced(
            layout,
            "Blockit (hex):  0x",
            land_entry_properties,
            "blockbit")

        layout.separator(factor=1)

        layout.prop(panel_settings, "advanced_surface_attributes")
        layout.prop(panel_settings, "land_entry_surface_attributes_editmode")

        SAIO_PT_LandEntry.draw_attributes(
            layout,
            land_entry_properties,
            panel_settings,
            panel_settings.advanced_surface_attributes)

    @staticmethod
    def draw_animated_properties(
            layout: bpy.types.UILayout,
            land_entry_properties: SAIO_LandEntry):

        layout.prop(land_entry_properties, "anim_start_frame")
        layout.prop(land_entry_properties, "anim_speed")

        prop_advanced(
            layout,
            "Texlist Pointer (hex):  0x",
            land_entry_properties,
            "tex_list_pointer"
        )


    @staticmethod
    def draw_land_entry_properties(
            layout: bpy.types.UILayout,
            is_level: bool,
            obj: bpy.types.Object,
            panel_settings: SAIO_PanelSettings):

        if not is_level:
            layout.box().label(text="Scene is not marked as a level")
            return

        land_entry_properties: SAIO_LandEntry = obj.saio_land_entry

        if obj.parent is not None:

            parent = obj.parent
            while parent.parent is not None:
                parent = parent.parent

            if parent.saio_land_entry.geometry_type == 'ANIMATED':
                layout.box().label(text="Part of animated object.")
                return

            elif parent.type == 'ARMATURE':
                layout.box().label(text="Part of an armature/animated object.")
                return

            else:
                geometry_type = 'STATIC'

        elif obj.type == 'ARMATURE':
            layout.box().label(text="Armature; Type is Animated.")
            geometry_type = 'ANIMATED'

        elif obj.type != 'MESH':
            layout.box().label(text="Not a mesh and does not qualify as level geometry.")
            return

        elif obj.parent is None and len(obj.children) == 0:
            layout.prop(land_entry_properties, "geometry_type")
            geometry_type = land_entry_properties.geometry_type

        else:
            layout.box().label(text="Not a root or as children; Type is Static.")
            geometry_type = 'STATIC'

        if geometry_type == 'STATIC':
            SAIO_PT_LandEntry.draw_static_properties(layout, land_entry_properties, panel_settings)
        else:
            SAIO_PT_LandEntry.draw_animated_properties(layout, land_entry_properties)

    # === overriden methods === #

    @classmethod
    def verify(cls, context: bpy.types.Context):

        error = SAIO_Scene.check_is_landtable(context)
        if error is not None:
            return error

        if context.active_object is None:
            return "No active object"

        return None

    def draw_panel(self, context):

        SAIO_PT_LandEntry.draw_land_entry_properties(
            self.layout,
            context.scene.saio_scene.scene_type == "LVL",
            context.active_object,
            context.scene.saio_scene.panels)
