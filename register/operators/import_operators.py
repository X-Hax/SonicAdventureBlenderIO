
import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import (
    BoolProperty,
    EnumProperty,
    StringProperty,
    CollectionProperty
)

from ...utils import get_default_path


class ImportOperator(bpy.types.Operator, ImportHelper):
    bl_options = {'PRESET', 'UNDO'}

    console_debug_output: BoolProperty(
        name="Console Output",
        description=(
            "Shows exporting progress in Console"
            " (Slows down Exporting Immensely)"
        ),
        default=False,
    )

    files: CollectionProperty(
        name='File paths',
        type=bpy.types.OperatorFileListElement
    )

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        self.filepath = get_default_path()
        wm = context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class SAIO_OT_Import_Model(ImportOperator):
    bl_idname = "saio.import_mdl"
    bl_label = "Sonic Adv. model (.*mdl)"

    filter_glob: StringProperty(
        default="*.sa1mdl;*.sa2mdl;*.sa2bmdl;",
        options={'HIDDEN'},
    )


class SAIO_OT_Import_Level(ImportOperator):
    bl_idname = "saio.import_lvl"
    bl_label = "Sonic Adv. Level (.*lvl)"

    filter_glob: StringProperty(
        default="*.sa1lvl;*.sa2lvl;*.sa2blvl;",
        options={'HIDDEN'},
    )

    fixView: BoolProperty(
        name="Adjust Clip Distance",
        description="Adjusts viewport clipping values.",
        default=False
    )
