import os
import bpy
from bpy.props import (
    BoolProperty,
    StringProperty,
    CollectionProperty,
)
from bpy.types import Context

from .base import SAIOBaseFileLoadOperator

from ...dotnet import load_dotnet, SAIO_NET


class ModelImportOperator(SAIOBaseFileLoadOperator):
    bl_options = {'PRESET', 'UNDO'}

    files: CollectionProperty(
        name='File paths',
        type=bpy.types.OperatorFileListElement
    )

    scene_per_file: BoolProperty(
        name="Scene per file",
        description="Create a new scene for each imported file",
        default=False
    )

    optimize: BoolProperty(
        name="Optimize",
        description="Merges vertices",
        default=False
    )

    @classmethod
    def poll(cls, context: Context):
        return context.mode == 'OBJECT'


class SAIO_OT_Import_Model(ModelImportOperator):
    bl_idname = "saio.import_mdl"
    bl_label = "Sonic Adv. model (.*mdl)"

    filter_glob: StringProperty(
        default="*.sa1mdl;*.sadxmdl;*.sa2mdl;*.sa2bmdl;*.nj;",
        options={'HIDDEN'},
    )

    import_as_armature: BoolProperty(
        name="Import as Armature",
        description="Import as an armature, even if the model is not weighted",
        default=False
    )

    merge_meshes: BoolProperty(
        name="Merge meshes",
        description=(
            "When importing an armature (whether forced or not), merge"
            " individual meshes into a single mesh"
        ),
        default=False
    )

    ensure_order: BoolProperty(
        name="Ensure sibling order",
        description=(
            "Ensure that objects retain order regardless of their imported"
            " name by prepending their global model Index to their name"
            " (e.g. 001_NodeName)"
        ),
        default=True
    )

    flip_vertex_colors: BoolProperty(
        name="Flip vertex colors",
        description=(
            "Some SA2 models use BGRA vertex colors, instead of AGBR."
            " Enabling this flips the channels."),
        default=False
    )

    def _execute(self, context):
        directory = os.path.dirname(self.filepath)

        load_dotnet()

        from ...importing import i_node

        scene = context.scene
        for file in self.files:

            filepath = os.path.join(directory, file.name)
            try:
                import_data = SAIO_NET.MODEL.Import(
                    filepath, self.optimize, self.flip_vertex_colors)
            except Exception as error:
                print(f"An error occured while importing {file.name}")
                raise error

            name = os.path.splitext(file.name)[0]
            if self.scene_per_file:
                scene = bpy.data.scenes.new(name)
                context.window.scene = scene

            scene.saio_scene.author = import_data.Author
            scene.saio_scene.description = import_data.Description

            collection = bpy.data.collections.new(name)
            scene.collection.children.link(collection)

            i_node.NodeProcessor.process_model(
                context,
                import_data,
                collection,
                file.name,
                None,
                None,
                self.import_as_armature,
                self.merge_meshes,
                self.ensure_order
            )

        return {'FINISHED'}


class SAIO_OT_Import_Landtable(ModelImportOperator):
    bl_idname = "saio.import_lvl"
    bl_label = "Sonic Adv. Landtable (.*lvl)"

    filter_glob: StringProperty(
        default="*.sa1lvl;*.sadxlvl;*.sa2lvl;*.sa2blvl;",
        options={'HIDDEN'},
    )

    fix_view: BoolProperty(
        name="Adjust Clip Distance",
        description="Adjusts viewport clipping values.",
        default=False
    )

    def _execute(self, context):
        directory = os.path.dirname(self.filepath)

        load_dotnet()
        from ...importing import i_landtable

        for file in self.files:
            filepath = os.path.join(directory, file.name)

            try:
                import_data = SAIO_NET.LANDTABLE_WRAPPER.Import(
                    filepath, self.optimize)
            except Exception as error:
                print(f"An error occured while importing {file.name}")
                raise error

            if self.scene_per_file:
                scene = bpy.data.scenes.new(file.name)
                context.window.scene = scene

            if self.fix_view:
                context.space_data.clip_start = 1.0
                context.space_data.clip_end = 10000.0

            i_landtable.LandtableProcessor.process_landtable(
                context,
                import_data,
                file.name,
                self.optimize)

        return {'FINISHED'}


class SAIO_OT_Import_Event(SAIOBaseFileLoadOperator):
    bl_idname = "saio.import_event"
    bl_label = "Import SA2 Event"
    bl_description = "Loads an sa2 event"
    bl_options = {'PRESET', 'UNDO'}

    filter_glob: StringProperty(
        default="*.prs",
        options={'HIDDEN'},
    )

    optimize: BoolProperty(
        name="Optimize",
        description="Optimize models and shapes from shape motions",
        default=True
    )

    @classmethod
    def poll(cls, context: Context):
        return context.mode == 'OBJECT'

    def _execute(self, context):
        load_dotnet()

        try:
            import_data = SAIO_NET.CUTSCENE.Import(
                self.filepath, self.optimize)
        except Exception as error:
            print(f"An error occured while importing {self.filepath}")
            raise error

        from os import path
        name = path.basename(path.splitext(self.filepath)[0])

        from ...importing import i_event
        importer = i_event.EventImporter(context, name, self.optimize)
        importer.process(import_data)
        return {'FINISHED'}
