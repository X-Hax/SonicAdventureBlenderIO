import bpy

from . import (
    scene_panel,
    landtable_panel,
    texture_panel,
    event_panel,
    texturename_panel
)


class ViewportScenePanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SAIO Scene"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def verify(cls, context):
        return cls.base.verify(context) # pylint: disable=no-member

    def draw(self, context):
        return self.base.draw(self, context) # pylint: disable=no-member

    def draw_panel(self, context):
        return self.base.draw_panel(self, context) # pylint: disable=no-member


class SAIO_PT_VSP_Settings(ViewportScenePanel):
    bl_label = "Settings"
    base = scene_panel.SAIO_PT_Scene


class SAIO_PT_VSP_Textures(ViewportScenePanel):
    bl_label = "Textures"
    base = texture_panel.SAIO_PT_SceneTextures


class SAIO_PT_VSP_Texturenames(ViewportScenePanel):
    bl_label = "Texture Names"
    base = texturename_panel.SAIO_PT_SceneTexturenames


class SAIO_PT_VSP_LandTable(ViewportScenePanel):
    bl_label = "Landtable"
    base = landtable_panel.SAIO_PT_Landtable


class SAIO_PT_VSP_Event(ViewportScenePanel):
    bl_label = "Event"
    base = event_panel.SAIO_PT_Event
