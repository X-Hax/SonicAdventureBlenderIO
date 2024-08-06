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


def register():
    """Loading API classes into blender"""

    for cls in classes:
        bpy.utils.register_class(cls)

    for cls in property_groups.to_register:
        if hasattr(cls, "register"):
            cls.register()

    bpy.utils.register_manual_map(manual.add_manual_map)


def unregister():
    """Unloading classes loaded in register(), as well as various cleanup"""

    unload_dotnet()

    bpy.utils.unregister_manual_map(manual.add_manual_map)

    for cls in classes:
        bpy.utils.unregister_class(cls)


def reload_package(module_dict_main):
    import importlib
    from pathlib import Path

    def reload_package_recursive(current_dir: Path, module_dict: dict[str, any]):
        for path in current_dir.iterdir():
            if "__init__" in str(path) or path.stem not in module_dict:
                continue

            if path.is_file() and path.suffix == ".py":
                importlib.reload(module_dict[path.stem])
            elif path.is_dir():
                reload_package_recursive(path, module_dict[path.stem].__dict__)

    reload_package_recursive(Path(__file__).parent, module_dict_main)
