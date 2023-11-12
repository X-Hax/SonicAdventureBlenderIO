import math
import bpy
import bmesh
from mathutils import Vector, Euler


def _normal_to_xz_angles(normal: Vector):

    close0 = abs(normal.x) < 0.0002 and abs(normal.y) < 0.0002
    if not close0:
        yrot = -math.pi - math.atan2(normal.x, normal.y)
    else:
        yrot = 0

    if normal.z > 0:
        if normal.z > 0.9999 or close0:
            xrot = 0
        else:
            xrot = math.acos(normal.z)
    elif normal.z < 0:
        if normal.z < -0.9999 or close0:
            xrot = math.pi
        else:
            xrot = math.asin(-normal.z) + math.pi * 0.5
    else:
        xrot = math.pi * 0.5

    return Euler((xrot, 0, yrot))


class PathProcessor:

    _name: str
    _positions: list[Vector]
    _normals: list[Vector]

    _curve_object: bpy.types.Object
    _curve: bpy.types.Curve
    _spline: bpy.types.Spline

    def __init__(self):
        self._name = None
        self._positions = None
        self._normals = None

        self._curve_object = None
        self._curve = None
        self._spline = None

    def _create_curve(self):
        self._curve = bpy.data.curves.new(self._name, 'CURVE')

        self._curve.resolution_u = 1
        self._curve.resolution_v = 1
        self._curve.extrude = 0.1
        self._curve.dimensions = '3D'
        self._curve.twist_mode = 'Z_UP'

        self._spline = self._curve.splines.new('BEZIER')
        self._curve_object = bpy.data.objects.new(self._name, self._curve)

    def _assemble_spline(self):

        # already has one point
        self._spline.bezier_points.add(len(self._positions) - 1)

        for i, point in enumerate(self._spline.bezier_points):
            point.co = self._positions[i]
            point.handle_left_type = 'AUTO'
            point.handle_right_type = 'AUTO'

    def _get_current_normals(self):
        mesh = self._curve_object.to_mesh()

        bm = bmesh.new() # pylint: disable=assignment-from-no-return
        bm.from_mesh(mesh)

        result: list[Vector] = [None] * int(len(mesh.vertices) / 2)
        for edge in bm.edges:
            v1 = edge.verts[0].index
            v2 = edge.verts[1].index

            if abs(v1 - v2) != 1:
                continue

            normal = sum(
                (f.normal for f in edge.link_faces), Vector()
            ).normalized()

            nrm_index = int(min(v1, v2) / 2)
            result[nrm_index] = normal

        bm.free()
        self._curve_object.to_mesh_clear()

        return result

    def _create_debug_object(self, name, position, normal):
        dbg = bpy.data.objects.new(self._name + name, None)
        dbg.location = position
        dbg.rotation_euler = _normal_to_xz_angles(normal)
        dbg.empty_display_type = 'SINGLE_ARROW'
        dbg.empty_display_size = 1
        bpy.context.scene.collection.objects.link(dbg)

    def _correct_normals(self):

        current_normals = self._get_current_normals()

        zipped = zip(
            current_normals,
            self._normals,
            self._spline.bezier_points)

        for cnrm, tnrm, point in zipped:
            tan = (point.handle_right - point.co).normalized()
            tnrm = tan.cross(tnrm)
            cnrm = tan.cross(cnrm)
            point.tilt = math.atan2(cnrm.cross(tnrm).dot(tan), cnrm.dot(tnrm))

    def process_spline(
            self,
            positions: list[Vector],
            normals: list[Vector],
            curve_object: bpy.types.Object,
            spline: bpy.types.Spline):

        self._positions = positions
        self._normals = normals
        self._curve_object = curve_object
        self._spline = spline

        self._assemble_spline()
        self._correct_normals()

    def process(
            self,
            name: str,
            positions: list[Vector],
            normals: list[Vector]):

        self._name = name
        self._positions = positions
        self._normals = normals

        self._create_curve()
        self._assemble_spline()
        self._correct_normals()

        self._curve.extrude = 1

        return self._curve_object
