import bpy
from bpy.props import (
    StringProperty,
    BoolProperty
)

from .base_import_operators import BaseImportModelOperator

from ...utility import progress_console
from ...utility.draw import col_prop
from ...external import SAIONET, enums, CModel, CLevel
from ...importing import i_level

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
            scene.saio_scene.internal_file_format = enums.FORMAT[model.format]
            scene.saio_scene.scene_type = 'MDL'

            collection = bpy.data.collections.new(model.name)
            scene.collection.children.link(collection)

            self.model_converter.convert_model(
                collection,
                model
            )

            self.mesh_converter.setup_materials(context)

            self.model_converter.reset()

        progress_console.update("Importing data")

        return {'FINISHED'}

class SAIO_OT_Import_Level(BaseImportModelOperator):
    """Load an SATools level file"""
    bl_idname = "saio.import_level"
    bl_label = "Sonic Adv. level (.*lvl)"

    fix_view: BoolProperty(
        name="Adjust Clip Distance",
        description="Adjusts viewport clipping values.",
        default=False
    )

    ensure_static_order: BoolProperty(
        name="Ensure model order",
        description=(
            "Ensure that level-models retain order regardless of their imported"
            " name by prepending their index to their name"
            " (e.g. 001_levelmodel_name)"
        ),
        default=True
    )

    def draw(self, context: bpy.types.Context):
        super().draw(context)
        self.draw_panel_level(self.layout)
        
    def draw_panel_level(self, layout: bpy.types.UILayout):
        header, body = layout.panel("SAIO_import_level")
        header.label(text="Level")

        if body:
            col_prop(body, self, "fix_view")
            col_prop(body, self, "ensure_static_order")

        return body

    def _setup(self, context):
        super()._setup(context)

        self.level_converter = i_level.LevelConverter(
            context,
            self.model_converter,
            self.mesh_converter,
            self.ensure_static_order
        )

    def import_(self, context):
        progress_console.update("Reading & converting model files")

        filepaths = self.get_files()
        
        levels = SAIONET.level_read_files(filepaths)
        scene = context.scene

        for level in levels:
            level: CLevel = level.contents

            if self.scene_per_file:
                scene = bpy.data.scenes.new(level.name)
                context.window.scene = scene

            if self.fix_view:
                context.space_data.clip_start = 1.0
                context.space_data.clip_end = 10000.0

            scene.saio_scene.author = level.author
            scene.saio_scene.description = level.description
            scene.saio_scene.chao_chunk = False
            scene.saio_scene.internal_file_format = enums.FORMAT[level.format]
            scene.saio_scene.scene_type = 'LVL'

            self.level_converter.convert_level(level)
            self.level_converter.reset()

        progress_console.update("Importing data")

        return {'FINISHED'}