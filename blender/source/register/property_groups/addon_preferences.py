import bpy
from bpy.props import BoolProperty, EnumProperty, IntProperty
from ...utility.draw import col_prop

class SAIO_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = '.'.join(__package__.split('.')[:3])

    enable_ginja: BoolProperty(
        name="Enable Ginja features",
        description="Enables importing and exporting the ginja format",
        default=False
    )

    multi_threading_mode: EnumProperty(
        name="Multi-threading mode",
        description="Whether and how to apply multi threading when e.g. exporting models",
        items=(
            ("AUTO", "Enabled - Automatic", "Use multi-threading. Automatically determine the number of thread to create"),
            ("LIMITED", "Enabled - Limited", "Use multi-threading. Limit the number threads to use (this can also be used to exceed the number of thread used by automatic)"),
            ("DISABLED", "Disabled", "Don't use multi-threading")
        ),
        default="AUTO"
    )

    multi_threading_limit: IntProperty(
        name="Multi-threading limit",
        description="The number of threads to limit processes to. This can also be used to exceed the number of thread used by automatic",
        min=2,
        soft_max=32,
        default=2
    )

    @property
    def dotnet_max_parallelism(self):
        if self.multi_threading_mode == 'AUTO':
            return -1
        elif self.multi_threading_mode == 'LIMITED':
            return self.multi_threading_limit
        else:
            return 0

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.separator(factor=0.5)

        col_prop(layout, self, "enable_ginja")
        layout.separator(type="LINE")

        layout.prop(self, "multi_threading_mode")
        if self.multi_threading_mode == 'LIMITED':
            layout.prop(self, "multi_threading_limit")

        layout.separator(factor=0.5)
            