"""Main entry point for the Sonic Adventure I/O blender addon"""

from .source import register as reg


def register():
    reg.register_classes()


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
