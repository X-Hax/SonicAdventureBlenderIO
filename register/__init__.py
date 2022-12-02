"""Blender operators, ui and property groups declared in this addon"""

import bpy
from . import (
    property_groups,
    addon_updater,
    operators,
    ui
)

classes = []

classes.extend(addon_updater.to_register)
classes.extend(property_groups.to_register)
classes.extend(operators.to_register)
classes.extend(ui.to_register)


def register_classes():
    """Loading API classes into blender"""

    for cls in classes:
        bpy.utils.register_class(cls)

    for cls in property_groups.to_register:
        cls.register()

    ui.register()


def unregister_classes():
    """Unloading classes loaded in register(), as well as various cleanup"""

    ui.unregister()

    for cls in classes:
        bpy.utils.unregister_class(cls)
