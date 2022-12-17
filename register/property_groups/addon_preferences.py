

import bpy
from bpy.props import (
    BoolProperty,
    IntProperty,
    StringProperty
)

from ..addon_updater import addon_updater_ops

from ... import utils


@addon_updater_ops.make_annotations
class SAIO_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = utils.__package__

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

    print_debug: BoolProperty(
        name="Print Debug",
        description=(
            "Prints debug info to output window,"
            " will slow down exports."
        ),
        default=False,
    )

    use_project_path: BoolProperty(
        name="Use Project Folder",
        description=(
            "Overrides the set Default Path if a Project File"
            " has been loaded."
        ),
        default=True
    )

    default_path: StringProperty(
        name="Default Path",
        description=(
            "Sets the default path used when importing/exporting files."
            " Defaults to user's documents folder if not set."
        ),
        default="",
        subtype='FILE_PATH'
    )

    tools_path: StringProperty(
        name="SA Tools Path",
        description="Path to your SA Tools install.",
        default="",
        subtype='FILE_PATH'
    )

    @classmethod
    def register(cls):
        pass

    def draw(self, context):
        layout = self.layout
        split = layout.split()
        split.prop(self, "print_debug")
        split.prop(self, "use_project_path")
        split = layout.split()
        split.prop(self, "tools_path")
        split.prop(self, "default_path")
        addon_updater_ops.update_settings_ui(self, context)
