import os
import bpy
from bpy.props import (
    StringProperty
)

from .base_import_operators import BaseImportModelOperator

from ...utility import progress_console
from ...external import SAIONET, CModel

class SAIO_OT_Import_Model(BaseImportModelOperator):
    """Load an SATools or ninja model file"""
    bl_idname = "saio.import_model"
    bl_label = "Sonic Adv. model (.*mdl/.nj)"

    filter_glob: StringProperty(
        default="*.sa1mdl;*.sadxmdl;*.sa2mdl;*.sa2bmdl;*.nj;",
        options={'HIDDEN'},
    )

    def import_(self, context):
        progress_console.update("Reading & converting model files")

        filepaths = self.get_files()

        models = SAIONET.model_read_files(filepaths)
        scene = context.scene

        for model in models:
            model: CModel = model.contents

            if self.scene_per_file:
                scene = bpy.data.scenes.new(model.name)
                context.window.scene = scene

            scene.saio_scene.author = model.author
            scene.saio_scene.description = model.description
            scene.saio_scene.chao_chunk = model.chao_chunk

            collection = bpy.data.collections.new(model.name)
            scene.collection.children.link(collection)

            self.node_converter.convert_model(
                collection,
                model
            )

            self.node_converter.reset()

        progress_console.update("Importing data")

        return {'FINISHED'}