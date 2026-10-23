"""Blender operators, ui and property groups declared in this addon"""

import bpy
from . import (
    property_groups,
    operators,
    ui,
    manual
)
from ..external import SAIONET
from ..exceptions import SAIOUserException

classes = []

classes.extend(property_groups.to_register)
classes.extend(operators.to_register)
classes.extend(ui.to_register)

MAPPING = None

def manual_hook():
    global MAPPING
    if MAPPING is None:
        MAPPING = manual.get_mapping(classes)
    return "https://x-hax.github.io/SonicAdventureBlenderIO/", MAPPING


def register():
    """Loading API classes into blender"""

    for cls in classes:
        if hasattr(cls, "class_setup"):
            cls.class_setup()

    for cls in classes:
        if not hasattr(cls, "DONT_REGISTER_CLASS"):
            bpy.utils.register_class(cls)
        elif hasattr(cls, "register"):
            cls.register()

    bpy.utils.register_manual_map(manual_hook)


def unregister():
    """Unloading classes loaded in register(), as well as various cleanup"""

    bpy.utils.unregister_manual_map(manual_hook)

    for cls in classes:
        if not hasattr(cls, "DONT_REGISTER_CLASS"):
            bpy.utils.unregister_class(cls)
        elif hasattr(cls, "unregister"):
            cls.unregister()

    if SAIONET._LIBRARY is not None:
        # Formatted to appear correctly for the user in blender,
        # as there seem to be no other means to display a message
        # when unregistering
        raise SAIOUserException(
            (
                "\n\n"
                "#===================================#\n"
                "#                                                                      #\n"
                "#     The external SAIO library is still loaded!    #\n"
                "#                                                                      #\n"
                "#         Please restart blender, and if you          #\n"
                "#    attempted to update: reinstall the addon     #\n"
                "#                                                                      #\n"
                "#===================================#"
            )
        )
    


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
