"""Main entry point for the Sonic Adventure I/O blender addon"""

import bpy
from .register import (
    addon_updater,
    register_classes,
    unregister_classes

)


bl_info = {
    "name": "Sonic Adventure I/O",
    "author": "X-Hax (Justin113D, ItsEasilyActually, Sora-yx)",
    "description": "Import/Exporter for the SA Models Formats.",
    "version": (2, 0, 0),
    "blender": (3, 3, 1),
    "location": "",
    "warning": "",
    "doc_url": "https://github.com/X-Hax/SonicAdventureBlenderIO/wiki",
    "tracker_url": (
        "https://github.com/X-Hax/SonicAdventureBlenderIO/issues/new"
    ),
    "category": "Import-Export"
}


def register():
    addon_updater.register(bl_info)
    register_classes()


def unregister():
    addon_updater.unregister()
    unregister_classes()


# When refreshing the addon, reload all modules
if locals().get('LOADED'):
    LOADED = False
    from importlib import reload
    from sys import modules

    modules[__name__] = reload(modules[__name__])
    to_reload = {}
    for name, module in modules.items():
        if name.startswith(f"{__package__}."):
            to_reload[name] = module

    for name, module in to_reload.items():
        globals()[name] = reload(module)

    del reload, modules

if __name__ == "__main__":
    register()

LOADED = True
