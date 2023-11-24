"""Blender operators, ui and property groups declared in this addon"""

import bpy
from . import (
    addon_updater,
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


def _install_pythondotnet():
    try:
        import pythonnet  # pylint: disable=unused-import
    except ModuleNotFoundError:
        import pip
        pip.main(["install", "pythonnet"])


def register_classes(bl_info):
    """Loading API classes into blender"""

    _install_pythondotnet()

    addon_updater.register_addon_updater(bl_info)

    for cls in classes:
        bpy.utils.register_class(cls)

    for cls in property_groups.to_register:
        if hasattr(cls, "register"):
            cls.register()

    bpy.utils.register_manual_map(manual.add_manual_map)


def unregister_classes():
    """Unloading classes loaded in register(), as well as various cleanup"""

    unload_dotnet()

    addon_updater.unregister_addon_updater()

    bpy.utils.unregister_manual_map(manual.add_manual_map)

    for cls in classes:
        bpy.utils.unregister_class(cls)
