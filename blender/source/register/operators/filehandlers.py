import bpy

from bpy_extras.io_utils import poll_file_object_drop


class SAIO_FH_SA1MDL(bpy.types.FileHandler):
    bl_idname = "SAIO_FH_sa1mdl"
    bl_label = "SA1 Model (.sa1mdl)"
    bl_import_operator = "saio.import_mdl"
    bl_export_operator = "saio.export_sa1mdl"
    bl_file_extensions = ".sa1mdl"

    @classmethod
    def poll_drop(cls, context):
        return poll_file_object_drop(context)


class SAIO_FH_SA2MDL(bpy.types.FileHandler):
    bl_idname = "SAIO_FH_sa2mdl"
    bl_label = "SA2 Model (.sa2mdl)"
    bl_import_operator = "saio.import_mdl"
    bl_export_operator = "saio.export_sa2mdl"
    bl_file_extensions = ".sa2mdl"

    @classmethod
    def poll_drop(cls, context):
        return poll_file_object_drop(context)


class SAIO_FH_SA2BMDL(bpy.types.FileHandler):
    bl_idname = "SAIO_FH_sa2bmdl"
    bl_label = "SA2B Model (.sa2bmdl)"
    bl_import_operator = "saio.import_mdl"
    bl_export_operator = "saio.export_sa2bmdl"
    bl_file_extensions = ".sa2bmdl"

    @classmethod
    def poll_drop(cls, context):
        return poll_file_object_drop(context)


class SAIO_FH_SA1LVL(bpy.types.FileHandler):
    bl_idname = "SAIO_FH_sa1lvl"
    bl_label = "SA1 Level (.sa1lvl)"
    bl_import_operator = "saio.import_lvl"
    bl_export_operator = "saio.export_sa1lvl"
    bl_file_extensions = ".sa1lvl"

    @classmethod
    def poll_drop(cls, context):
        return poll_file_object_drop(context)


class SAIO_FH_SA2LVL(bpy.types.FileHandler):
    bl_idname = "SAIO_FH_sa2lvl"
    bl_label = "SA2 Level (.sa2lvl)"
    bl_import_operator = "saio.import_lvl"
    bl_export_operator = "saio.export_sa2lvl"
    bl_file_extensions = ".sa2lvl"

    @classmethod
    def poll_drop(cls, context):
        return poll_file_object_drop(context)


class SAIO_FH_SA2BLVL(bpy.types.FileHandler):
    bl_idname = "SAIO_FH_sa2blvl"
    bl_label = "SA2B Level (.sa2blvl)"
    bl_import_operator = "saio.import_lvl"
    bl_export_operator = "saio.export_sa2blvl"
    bl_file_extensions = ".sa2blvl"

    @classmethod
    def poll_drop(cls, context):
        return poll_file_object_drop(context)
