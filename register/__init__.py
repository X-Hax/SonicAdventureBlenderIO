"""Blender operators, ui and property groups declared in this addon"""

import bpy
from . import (
    addon_updater,
    property_groups,
    operators,
    ui
)

classes = []

classes.extend(property_groups.to_register)
classes.extend(operators.to_register)
classes.extend(ui.to_register)


def register_classes(bl_info):
    """Loading API classes into blender"""

    addon_updater.register_addon_updater(bl_info)

    for cls in classes:
        bpy.utils.register_class(cls)

    for cls in property_groups.to_register:
        cls.register()

    ui.register()


def unregister_classes():
    """Unloading classes loaded in register(), as well as various cleanup"""

    addon_updater.unregister_addon_updater()

    ui.unregister()

    for cls in classes:
        bpy.utils.unregister_class(cls)
