import bpy

from ..utility import math_utils
from ..exceptions import UserException
from ..dotnet import load_dotnet, System, SAIO_NET

DEFAULT_CURVE_CONFIG = {
    "offset": 0,
    "extrude": 0.1,
    "taper_object": None,
    "bevel_mode": 'ROUND',
    "bevel_depth": 0,
    "bevel_factor_start": 0,
    "bevel_factor_end": 1,
}


class PathEvaluator:

    _curve_object: bpy.types.Object
    _curve: bpy.types.Curve
    _prev_params: dict[str, any]

    def __init__(self):
        self._curve = None
        self._prev_params = None

    def _verify_curve(self):
        if len(self._curve.splines) == 0:
            raise UserException("Curve has no splines! Expecting 1!")
        elif len(self._curve.splines) > 1:
            raise UserException("Curve has multiple splines! Expecting 1!")

    def _prepare_curve(self):
        self._prev_params = {}
        for name, value in DEFAULT_CURVE_CONFIG.items():
            self._prev_params[name] = getattr(self._curve, name)
            setattr(self._curve, name, value)

    def _cleanup_curve(self):
        for name, value in self._prev_params.items():
            setattr(self._curve, name, value)

    def evaluate_path(self, curve_object: bpy.types.Object):

        load_dotnet()

        self._curve_object = curve_object
        self._curve = curve_object.data

        self._verify_curve()
        self._prepare_curve()

        try:
            mesh = self._curve_object.to_mesh()

            matrix = curve_object.matrix_world
            normal_matrix = math_utils.get_normal_matrix(matrix)

            positions = []
            normals = []

            iterator = iter(mesh.vertices)
            for v1 in iterator:
                v2 = next(iterator)

                pos = matrix @ ((v1.co + v2.co) * 0.5)
                nrm = normal_matrix @ ((v1.normal + v2.normal).normalized())

                positions.append(System.VECTOR3(pos.x, pos.z, -pos.y))
                normals.append(System.VECTOR3(nrm.x, nrm.z, -nrm.y))

            result = SAIO_NET.CURVE_PATH.FromPoints(positions, normals)

            self._curve_object.to_mesh_clear()
        finally:
            self._cleanup_curve()

        return result
