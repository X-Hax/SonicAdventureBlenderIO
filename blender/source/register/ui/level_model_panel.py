import bpy

from .base_panel import PropertiesPanel

from ..property_groups.scene_properties import SAIO_Scene
from ..property_groups.level_model_properties import (
    SAIO_LevelModel, 
    SA1_SURFACE_ATTRIBUTES,
    SA2_VISUAL_SURFACE_ATTRIBUTES,
    SA2_COLLISION_SURFACE_ATTRIBUTES
)

from ...utility.general import get_addon_preferences

class SAIO_PT_LevelModel(PropertiesPanel):
    bl_label = "SAIO Level-Model Properties"
    bl_context = "object"

    @staticmethod
    def draw_surface_attribute_grid(
        layout: bpy.types.UILayout,
        data: SAIO_LevelModel,
        attribute_info: list[tuple[str, str, list[int] | None, str]],
        property_prefix: str,
        show_unknown: bool,
        type_filter: str | None):

        grid = layout.grid_flow(row_major=True, even_columns=True, even_rows=True, align=True)
        for i, attribute in enumerate(attribute_info):

            if attribute is None and not show_unknown:
                continue

            if type_filter is not None and attribute[3] != type_filter:
                continue

            attribute_layout = grid.row(align=True)

            attribute_layout.active = (
                attribute is None 
                or len(attribute) < 3
                or attribute[2] is None
                or any([getattr(data, property_prefix + str(x)) for x in attribute[2]])
            )

            property = property_prefix + str(i)
            text = data.bl_rna.properties[property].name
            attribute_layout.prop(data, property, text=f"        {text}        ", toggle=True)

    @staticmethod
    def draw_static_properties(
        layout: bpy.types.UILayout,
        file_format: str,
        show_unknown_attributes: bool,
        level_model_properties: SAIO_LevelModel):

        layout.prop(level_model_properties, "blockbit_hex")
        
        header, menu = layout.panel("saio_visual_surface_attributes")
        header.label(text="Visual surface attributes")
        if menu:
            if file_format == 'BASIC':
                SAIO_PT_LevelModel.draw_surface_attribute_grid(
                    menu,
                    level_model_properties,
                    SA1_SURFACE_ATTRIBUTES,
                    "sa1_surface_attribute_",
                    show_unknown_attributes,
                    "VIS"
                )
            else:
                SAIO_PT_LevelModel.draw_surface_attribute_grid(
                    menu,
                    level_model_properties,
                    SA2_VISUAL_SURFACE_ATTRIBUTES,
                    "sa2_visual_surface_attribute_",
                    show_unknown_attributes,
                    None
                )

        header, menu = layout.panel("saio_collision_surface_attributes")
        header.label(text="Collision surface attributes")

        if menu:
            if file_format == 'BASIC':
                SAIO_PT_LevelModel.draw_surface_attribute_grid(
                    menu,
                    level_model_properties,
                    SA1_SURFACE_ATTRIBUTES,
                    "sa1_surface_attribute_",
                    show_unknown_attributes,
                    "COL"
                )
            else:
                SAIO_PT_LevelModel.draw_surface_attribute_grid(
                    menu,
                    level_model_properties,
                    SA2_COLLISION_SURFACE_ATTRIBUTES,
                    "sa2_collision_surface_attribute_",
                    show_unknown_attributes,
                    None
                )


    @staticmethod
    def draw_level_model_properties(
            layout: bpy.types.UILayout,
            is_level: bool,
            file_format: str,
            show_unknown_attributes: bool,
            obj: bpy.types.Object):

        if not is_level:
            layout.box().label_multiline(text="Scene is not marked as a level")
            return

        layout.use_property_split = False
        layout.use_property_decorate = False

        (geometry_type, info) = SAIO_LevelModel.evaluate_geometry_type(obj)

        if info is None:
            layout.prop(obj.saio_level_model, "geometry_type")
        else:
            layout.box().label_multiline(text=info)

        if geometry_type == 'STATIC':
            SAIO_PT_LevelModel.draw_static_properties(layout, file_format, show_unknown_attributes, obj.saio_level_model)
        elif geometry_type == 'ANIMATED':
            pass

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
        preferences = get_addon_preferences(context)

        SAIO_PT_LevelModel.draw_level_model_properties(
            self.layout,
            context.scene.saio_scene.scene_type == "LVL",
            context.scene.saio_scene.file_format,
            preferences.show_unknown_surface_attributes,
            context.active_object
        )