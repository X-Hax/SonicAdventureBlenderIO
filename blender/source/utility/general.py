import os
import bpy
import platform
import struct
from ..register.property_groups.addon_preferences import SAIO_AddonPreferences

from os.path import dirname

ADDON_DIR = dirname(dirname(dirname(os.path.realpath(__file__))))
ADDON_NAME = os.path.basename(ADDON_DIR)
PACKAGE_NAME = '.'.join(__package__.split('.')[:3])
ICON_DIR = os.path.join(ADDON_DIR, "icons")

def is_arm():
    return 'arm' in platform.machine().lower()

def is_x64():
    return struct.calcsize("P") == 8

def get_addon_preferences(context: bpy.types.Context | None = None) -> SAIO_AddonPreferences:
    if context is None:
        context = bpy.context
    return context.preferences.addons[PACKAGE_NAME].preferences