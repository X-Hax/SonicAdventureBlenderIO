import bpy
from bpy.props import StringProperty, EnumProperty, BoolProperty
from bpy.types import Context
from mathutils import Vector

from . import base

from ...importing.i_path import PathProcessor
from ...exporting.o_path import PathEvaluator
from ...utility import math_utils
from ...utility.draw import prop_advanced
from ...exceptions import UserException
from ...dotnet import load_dotnet, SAIO_NET


PATH_CODE_LUT = {
    'SA1L': 0x4BB1F0,
    'SA2L': 0x497B50,
    'SA2R': 0x4980C0,
    'SA2H': 0x498140,
}


def _enable_curve_normals(context: bpy.types.Context):
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.overlay.show_curve_normals = True


class SAIO_OT_Import_Path(base.SAIOBaseFileLoadOperator):
    bl_idname = "saio.import_path"
    bl_label = "Import Path (.ini)"
    bl_description = "Import a path from an ini file"
    bl_options = {'UNDO'}

    filter_glob: StringProperty(
        default="*.ini",
        options={'HIDDEN'},
    )

    @classmethod
    def poll(cls, context: Context):
        return context.mode == 'OBJECT'

    def _execute(self, context: bpy.types.Context):
        load_dotnet()

        pathdata = SAIO_NET.PATH_DATA.ReadINIFile(self.filepath)
        points = SAIO_NET.CURVE_PATH.ToPoints(pathdata)

        positions = [Vector((p.X, -p.Z, p.Y)) for p in points.Item1]
        normals = [Vector((n.X, -n.Z, n.Y)) for n in points.Item2]

        from os import path
        name = path.basename(self.filepath)

        processor = PathProcessor()
        curve_object = processor.process(
            name,
            positions,
            normals)

        context.scene.collection.objects.link(curve_object)
        _enable_curve_normals(context)

        return {'FINISHED'}


class SAIO_OT_Path_Generate(base.SAIOBaseOperator):
    bl_idname = "saio.path_generate"
    bl_label = "Generate Path"
    bl_description = (
        "Generates an Adventure games formatted path from a selected mesh."
    )
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return (
            context.mode == 'EDIT_MESH'
            and context.active_object.data.total_edge_sel > 0)

    def _get_vertices_in_order(self, context):
        mesh: bpy.types.Mesh = context.active_object.data

        edge_map: dict[int, list[int]] = {}

        for edge in mesh.edges:
            if not edge.select:
                continue

            v1 = edge.vertices[0]
            v2 = edge.vertices[1]

            if v1 not in edge_map:
                edge_map[v1] = []

            if v2 not in edge_map:
                edge_map[v2] = []

            edge_map[v1].append(v2)
            edge_map[v2].append(v1)

        start = None
        for vi, connected in edge_map.items():
            if len(connected) == 1:
                start = vi
                break

        if start is None:
            start = min(edge_map.keys())

        result = []
        used = set()
        while start is not None:
            result.append(mesh.vertices[start])
            used.add(start)

            connections = edge_map[start]
            start = None
            for vi in connections:
                if vi not in used:
                    start = vi
                    break

        if len(used) != len(edge_map):
            raise UserException("Selected edges do not form a single line!")

        return result

    def _execute(self, context):

        bpy.ops.object.mode_set(mode='OBJECT')
        context.view_layer.update()

        try:
            vertices = self._get_vertices_in_order(context)
        except UserException as ue:
            bpy.ops.object.mode_set(mode='EDIT')
            raise ue

        positions = []
        normals = []

        matrix = context.active_object.matrix_world
        normal_matrix = math_utils.get_normal_matrix(matrix)

        for vertex in vertices:
            positions.append(matrix @ vertex.co)
            normals.append(normal_matrix @ vertex.normal)

        processor = PathProcessor()
        curve_object = processor.process(
            context.active_object.data.name + "_curve",
            positions,
            normals)

        context.scene.collection.objects.link(curve_object)
        _enable_curve_normals(context)

        bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}


class SAIO_OT_Export_Path(base.SAIOBaseFileSaveOperator):
    bl_idname = "saio.export_path"
    bl_label = "Export Path (.ini/.c)"
    bl_description = "Export a path to an ini/c struct file"

    filename_ext = ".ini"

    filter_glob: StringProperty(
        default="*.ini;*.c;",
        options={'HIDDEN'}
    )

    format: EnumProperty(
        name="Format",
        description="Export to ini or C formatted file.",
        items=(
                        ('INI', "INI format", "Export to ini formatted file"),
                        ('C', "C struct", "Export to C formatted file.")
        ),
        default='INI'
    )

    struct_use_path: BoolProperty(
        name="Use path structs",
        description=(
            "C export uses Loop and Loophead by default. Checking this will"
            " export with pathtbl and pathtag instead."
        ),
        default=False
    )

    curve_type: EnumProperty(
        name="Curve Code",
        description="Set the Code address for the Path to use in-game.",
        items=(
            ('USER', "Custom Code",
             "Uses the code address supplied in the below textbox. Defaults to"
             " 0 if no address is supplied."),

            ('SA1L', "SA1 Loops",
             "Used on most paths where the player is moved, ie Loops."),

            ('SA2L', "SA2 Loops",
             "Used on most paths where the player is moved, ie Loops."),

            ('SA2R', "SA2 Grind Rails",
             "Used for most grind rails."),

            ('SA2H', "SA2 Hand Rails",
             "Used for the hand/gravity rails used in Crazy Gadget.")
        ),
        default='USER'
    )

    custom_code: StringProperty(
        name="Custom Code Address",
        description="Supply a custom code address (in hex)",
        default="0",
    )

    def draw(self, context: Context):
        super().draw(context)
        self.draw_panel_format(self.layout)
        self.draw_panel_type(self.layout)

    def draw_panel_format(self, layout: bpy.types.UILayout):
        header, body = layout.panel(
            "SAIO_export_path_format", default_closed=True)
        header.label(text="Format")

        if body:
            body.prop(self, "format")

            if self.format == 'C':
                body.prop(self, "struct_use_path")

        return body

    def draw_panel_type(self, layout: bpy.types.UILayout):
        header, body = layout.panel(
            "SAIO_export_path_type", default_closed=True)
        header.label(text="Type")

        if body:
            body.prop(self, "curve_type")

            if self.curve_type == 'USER':
                prop_advanced(
                    layout,
                    "Custom Code Address (Hex): 0x",
                    self,
                    "custom_code")
            else:
                layout.label(
                    text=f"Code: 0x{PATH_CODE_LUT[self.curve_type]:X}")

        return body

    @classmethod
    def poll(cls, context):
        return (
            context.mode == 'OBJECT'
            and context.active_object is not None
            and context.active_object.type == 'CURVE')

    def check(self, context: Context) -> bool:
        if self.format == 'C':
            self.filename_ext = '.c'
        else:
            self.filename_ext = '.ini'

        return super().check(context)

    def _execute(self, context: bpy.types.Context):
        load_dotnet()

        evaluator = PathEvaluator()
        path = evaluator.evaluate_path(context.active_object)

        if self.curve_type == 'USER':
            try:
                path.Code = int(self.custom_code, base=16)
            except Exception:
                pass
        else:
            path.Code = PATH_CODE_LUT[self.curve_type]

        if self.format == 'INI':
            path.WriteINIFile(self.filepath)
        else:
            path.ToCodeFile(self.filepath, self.struct_use_path)

        return {'FINISHED'}
