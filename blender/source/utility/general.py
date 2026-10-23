import os
import bpy
import platform
import struct

from os.path import dirname

ADDON_DIR = dirname(dirname(dirname(os.path.realpath(__file__))))
ADDON_NAME = os.path.basename(ADDON_DIR)
PACKAGE_NAME = '.'.join(__package__.split('.')[:3])
ICON_DIR = os.path.join(ADDON_DIR, "icons")

def is_arm():
    return 'arm' in platform.machine().lower()

def is_x64():
    return struct.calcsize("P") == 8

