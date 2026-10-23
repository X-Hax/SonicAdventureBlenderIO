"""Main entry point for the Sonic Adventure I/O blender addon"""

if "register" in locals():
    from .source.register import reload_package
    reload_package(locals())

from .source.register import register, unregister

bl_info = {
    "name": "Sonic Adventure I/O DEV BUILD",
    "author": "Justin113D, ItsEasyActually, X-Hax",
    "description": "Import/Exporter for Sonic Adventure Model, Animation and other Formats.",
    "version": (2, 999, 0),
    "blender": (5, 2, 0),
    "doc_url": "https://x-hax.github.io/SonicAdventureBlenderIO/",
    "tracker_url": "https://github.com/X-Hax/SonicAdventureBlenderIO/issues/new",
    "category": "Import-Export"
}
