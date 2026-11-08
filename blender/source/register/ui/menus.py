import bpy

from ..operators.import_operators import (
    SAIO_OT_Import_Model
)


class TOPBAR_MT_SAIO_Import(bpy.types.Menu):
    '''The SAIO submenu in the import menu'''
    bl_label = "SAIO Formats"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Import...")
        layout.operator(SAIO_OT_Import_Model.bl_idname)

    @staticmethod
    def menu_func(self, context):
        self.layout.menu(TOPBAR_MT_SAIO_Import.__name__)

    @classmethod
    def register(cls):
        bpy.types.TOPBAR_MT_file_import.append(TOPBAR_MT_SAIO_Import.menu_func)

    @classmethod
    def unregister(cls):
        bpy.types.TOPBAR_MT_file_import.remove(TOPBAR_MT_SAIO_Import.menu_func)