from . import addon_updater_ops


def register_addon_updater(bl_info):
    addon_updater_ops.register(bl_info)


def unregister_addon_updater():
    addon_updater_ops.unregister()
