import bpy
from ..operators.export_operators import (
    SAIO_OT_Export_SA1MDL,
    SAIO_OT_Export_SA2MDL,
    SAIO_OT_Export_SA2BMDL,
    SAIO_OT_Export_SA1LVL,
    SAIO_OT_Export_SA2LVL,
    SAIO_OT_Export_SA2BLVL,
    SAIO_OT_Export_Event,
)

from ..operators.import_operators import (
    SAIO_OT_Import_Model,
    SAIO_OT_Import_Landtable,
    SAIO_OT_Import_Event
)


class TOPBAR_MT_SAIO_Export(bpy.types.Menu):
    '''The saio submenu in the export menu'''
    bl_label = "SAIO Formats"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Export as...")
        layout.operator(SAIO_OT_Export_SA1MDL.bl_idname)
        layout.operator(SAIO_OT_Export_SA2MDL.bl_idname)
        layout.operator(SAIO_OT_Export_SA2BMDL.bl_idname)
        layout.separator()
        layout.operator(SAIO_OT_Export_SA1LVL.bl_idname)
        layout.operator(SAIO_OT_Export_SA2LVL.bl_idname)
        layout.operator(SAIO_OT_Export_SA2BLVL.bl_idname)
        layout.separator()
        layout.operator(SAIO_OT_Export_Event.bl_idname)

    @staticmethod
    def menu_func(self, context):
        self.layout.menu(TOPBAR_MT_SAIO_Export.__name__)

    @classmethod
    def register(cls):
        bpy.types.TOPBAR_MT_file_export.append(TOPBAR_MT_SAIO_Export.menu_func)

    @classmethod
    def unregister(cls):
        bpy.types.TOPBAR_MT_file_export.remove(TOPBAR_MT_SAIO_Export.menu_func)


class TOPBAR_MT_SAIO_Import(bpy.types.Menu):
    '''The saio submenu in the import menu'''
    bl_label = "SAIO Formats"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Import as...")
        layout.operator(SAIO_OT_Import_Model.bl_idname)
        layout.operator(SAIO_OT_Import_Landtable.bl_idname)
        layout.operator(SAIO_OT_Import_Event.bl_idname)

    @staticmethod
    def menu_func(self, context):
        self.layout.menu(TOPBAR_MT_SAIO_Import.__name__)

    @classmethod
    def register(cls):
        bpy.types.TOPBAR_MT_file_import.append(TOPBAR_MT_SAIO_Import.menu_func)

    @classmethod
    def unregister(cls):
        bpy.types.TOPBAR_MT_file_import.remove(TOPBAR_MT_SAIO_Import.menu_func)
