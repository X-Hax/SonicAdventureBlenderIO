import os
import bpy
from bpy.props import (
    BoolProperty,
    StringProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty
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

    all_weighted_meshes: BoolProperty(
        name="All weighted meshes",
        description=(
            "When importing and armature (whether forced or not), import"
            " all meshes as weighted meshes, even if they are weighted to"
            " only one bone and could just be parented"
        )
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
                self.all_weighted_meshes,
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

    ensure_static_order: BoolProperty(
        name="Ensure landentry order",
        description=(
            "Ensure that landentries retain order regardless of their imported"
            " name by prepending their entry index to their name"
            " (e.g. 001_landentry_name)"
        ),
        default=True
    )

    ###################################

    show_anim: BoolProperty(
        name="Animation",
        default=False
    )

    ###################################

    rotation_mode: EnumProperty(
        name="Rotation Mode",
        description="How rotations should be imported",
        items=(
            ("ANIM", "Animation", "Adjust bone rotation modes to match the"
             " animation"),
            ("KEEP", "Keep", "Import into bone rotation modes"),
        ),
        default="ANIM"
    )

    quaternion_threshold: FloatProperty(
        name="Quaternion conversion deviation threshold",
        description=(
            "If the animations rotation data doesnt match the bones"
            " rotation mode, the data will have to be converted. converting"
            " between euler and quaternion rotations is inaccurate, as the"
            " interpolation between those types is not linear. This value"
            " determines the threshold, from which a keyframe should be"
            " removed. 0 means all interpolated keyframes, 1 means none."
            " usually, a value around 0.05 is enough and gets rid of most"
            " unnecessary keyframes"
        ),
        default=0,
        min=0
    )

    short_rot: BoolProperty(
        name="Read as 16 bit rotations",
        description=(
            "Fallback value. Only required to be set if the file version is 0"
        ),
        default=False
    )

    show_advanced_anim: BoolProperty(
        name="Advanced Animation",
        default=False
    )

    ###################################

    def draw(self, context: Context):
        layout = self.layout

        layout.prop(self, "scene_per_file")
        layout.prop(self, "optimize")
        layout.prop(self, "fix_view")
        layout.prop(self, "ensure_static_order")

        header, box = layout.panel("saio_ot_lvli_animation", default_closed=True)
        header.label(text="Animation")
        if box:
            box.prop(self, "all_weighted_meshes")
            box.prop(self, "merge_meshes")
            box.prop(self, "ensure_order")

            box.separator()

            box.prop(self, "rotation_mode")

            header2, box2 = box.panel("saio_ot_lvli_advanced", default_closed=True)
            header2.label(text="Advanced")
            if box2:
                box2.prop(self, "quaternion_threshold")
                box2.prop(self, "short_rot")


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
                self.optimize,
                self.ensure_static_order,
                self.all_weighted_meshes,
                self.merge_meshes,
                self.ensure_order,
                self.rotation_mode,
                self.quaternion_threshold,
                self.short_rot)

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
