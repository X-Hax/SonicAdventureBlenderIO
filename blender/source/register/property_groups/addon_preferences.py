import bpy
from bpy.props import (
    BoolProperty,
    IntProperty,
    StringProperty
)

from ..addon_updater import addon_updater_ops


@addon_updater_ops.make_annotations
class SAIO_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__.split('.')[0]

    auto_check_update = BoolProperty(
        name="Auto-check for Update",
        description="If enabled, auto-check for updates using an interval",
        default=False)

    updater_interval_months = IntProperty(
        name='Months',
        description="Number of months between checking for updates",
        default=0,
        min=0)

    updater_interval_days = IntProperty(
        name='Days',
        description="Number of days between checking for updates",
        default=7,
        min=0,
        max=31)

    updater_interval_hours = IntProperty(
        name='Hours',
        description="Number of hours between checking for updates",
        default=0,
        min=0,
        max=23)

    updater_interval_minutes = IntProperty(
        name='Minutes',
        description="Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59)

    def draw(self, context):
        addon_updater_ops.update_settings_ui(self, context)
