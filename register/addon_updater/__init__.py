from . import (
    addon_updater_ops,
    preferences
)

to_register = [
    preferences.AddonPreferences
]


def register(bl_info):
    addon_updater_ops.register(bl_info)


def unregister():
    addon_updater_ops.unregister()
