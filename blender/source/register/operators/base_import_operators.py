import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    CollectionProperty,
    FloatProperty
)

from .base_operators import SAIOBaseFileLoadOperator

from ...external import SAIONET
from ...importing import i_mesh, i_model
from ...utility import progress_console
from ...utility.general import get_addon_preferences
from ...utility.draw import col_prop

class BaseImportOperator(SAIOBaseFileLoadOperator):
    bl_options = {'PRESET', 'UNDO'}

    files: CollectionProperty(
        name='File paths',
        type=bpy.types.OperatorFileListElement
    )

    def draw(self, context):
        self.layout.use_property_split = True
        self.layout.use_property_decorate = False

    def _execute(self, context: bpy.types.Context):
        with SAIONET.load():

            self.addon_preference = get_addon_preferences(context)
            self._setup(context)

            progress_console.cleanup()
            progress_console.start("Importing")
            result = self.import_(context)
            progress_console.end()

            return result

    def _setup(self, context: bpy.types.Context):
        pass

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.mode == 'OBJECT'

class BaseImportModelOperator(BaseImportOperator):
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

    ensure_sibling_order: BoolProperty(
        name="Ensure sibling order",
        description=(
            "Ensure that objects retain order regardless of their imported"
            " name by prepending their global model Index to their name"
            " (e.g. 001_NodeName)"
        ),
        default=True
    )

    force_armature: BoolProperty(
        name="Force armature",
        description="Force import the model as an armature, if it has more than one node",
        default=False
    )

    bone_orientation: EnumProperty(
        name="Bone orientation",
        description="How nodes should be converted into armature-bone space",
        items=(
            ('DEFAULT', "Default", "Import them with the same orientation like objects"),
            ('XZ', "XZ", "TODO")
        )
    )

    bone_length_mode: EnumProperty(
        name="Bone length mode",
        description="How to determine a bones length",
        items=(
            ('CLOSEST', "Closest", "Use distance to closest bone for length"),
            ('FURTHEST', "Furthest", "Use distance to farthest bone for length"),
            ('MOSTCHILDREN', "Most Children",
             "Use distance to the child with most children itself for length"),
            ('FIRST', "First", "Use distance to the first child for length"),
        ),
        default='MOSTCHILDREN'
    )

    min_bone_length: FloatProperty(
        name="Minimum bone length",
        description="The minimum length a bone should have",
        min=0.01,
        default=0.01
    )

    max_leaf_bone_length: FloatProperty(
        name="Maximum leaf bone length",
        description="The maximum length a bone with no children should have",
        min=0.01,
        default=1
    )

    armature_mesh_mode: EnumProperty(
        name="Armature mesh mode",
        description="How meshes should be imported to armatures",
        items=(
            ('DEFAULT', "Default", "Import meshes as is, and parent them to bones if they are not weighted"),
            ('WEIGHTED', "Force weights", "Force all meshes to use weights"),
            ('MERGE', "Merge", "Merge all meshes on an armature into one mesh")
        )
    )

    def draw(self, context: bpy.types.Context):
        super().draw(context)

        col_prop(self.layout, self, "scene_per_file")
        self.draw_panel_node(self.layout)
        self.draw_panel_mesh(self.layout)

    def draw_panel_node(self, layout: bpy.types.UILayout):
        header, body = layout.panel("SAIO_import_model_node")
        header.label(text="Model")

        if body:
            col_prop(body, self, "ensure_sibling_order")

            self.draw_panel_armature(body)

        return body

    def draw_panel_armature(self, layout: bpy.types.UILayout):
        header, body = layout.panel("SAIO_import_model_armature")
        header.label(text="Armature")

        if body:
            col_prop(body, self, "force_armature")
            body.prop(self, "bone_orientation")
            body.prop(self, "bone_length_mode")
            body.prop(self, "min_bone_length")
            body.prop(self, "max_leaf_bone_length")

        return body

    def draw_panel_mesh(self, layout: bpy.types.UILayout):
        header, body = layout.panel("SAIO_import_model_mesh")
        header.label(text="Mesh")

        if body:
            body.prop(self, "armature_mesh_mode")

        return body

    def _setup(self, context):
        super()._setup(context)

        self.mesh_converter = i_mesh.MeshConverter(
            self.armature_mesh_mode != 'DEFAULT'
        )

        self.node_converter = i_model.ModelConverter(
            self.mesh_converter,
            context,
            self.ensure_sibling_order,
            self.force_armature,
            self.bone_orientation,
            self.bone_length_mode,
            self.min_bone_length,
            self.max_leaf_bone_length,
            self.armature_mesh_mode == 'MERGE'
        )