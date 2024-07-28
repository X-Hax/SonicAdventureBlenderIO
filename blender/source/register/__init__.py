"""Blender operators, ui and property groups declared in this addon"""

import bpy
from . import (
    property_groups,
    operators,
    ui,
    manual
)

from ..dotnet import unload_dotnet

classes = []

classes.extend(property_groups.to_register)
classes.extend(operators.to_register)
classes.extend(ui.to_register)


def register_classes():
    """Loading API classes into blender"""

    for cls in classes:
        bpy.utils.register_class(cls)

    for cls in property_groups.to_register:
        if hasattr(cls, "register"):
            cls.register()

    bpy.utils.register_manual_map(manual.add_manual_map)


def unregister_classes():
    """Unloading classes loaded in register(), as well as various cleanup"""

    unload_dotnet()

    bpy.utils.unregister_manual_map(manual.add_manual_map)

    for cls in classes:
        bpy.utils.unregister_class(cls)
