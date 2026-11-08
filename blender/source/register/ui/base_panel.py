import bpy

from ...utility.draw import draw_error_box


class PropertiesPanel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def verify(cls, context: bpy.types.Context) -> str | None:
        return None

    def draw_panel(self, context: bpy.types.Context):
        return

    def draw(self, context: bpy.types.Context):

        if draw_error_box(self.layout, self.verify(context)):
            return

        self.draw_panel(context)
