"""Main entry point for the Sonic Adventure I/O blender addon"""

from .source import register as reg

bl_info = {
    "name": "Sonic Adventure I/O TEST BUILD",
    "author": "Justin113D, ItsEasyActually, X-Hax",
    "description": "Import/Exporter for Sonic Adventure Model, Animation and other Formats.",
    "version": (2, 2, 0),
    "blender": (4, 2, 0),
    "location": "",
    "warning": "",
    "doc_url": "https://x-hax.github.io/SonicAdventureBlenderIO/",
    "tracker_url": "https://github.com/X-Hax/SonicAdventureBlenderIO/issues/new",
    "category": "Import-Export"
}


def register():
    reg.register_classes(bl_info)


def unregister():
    reg.unregister_classes()


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
