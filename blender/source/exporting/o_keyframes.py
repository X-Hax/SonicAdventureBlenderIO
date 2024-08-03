import math
import bpy
from bpy.types import FCurve, Action
from mathutils import Vector, Matrix, Quaternion, Euler

from . import o_matrix
from .o_mesh import ModelMesh

from ..utility import camera_utils
from ..utility.anim_parameters import AnimParameters
from ..dotnet import System, SA3D_Common, SA3D_Modeling
from ..exceptions import UserException


class KeyframeEvaluator:

    _start: int
    _end: int
    _anim_parameters: AnimParameters

    _is_quat: bool
    _obj_rotation_mode: str
    _rotate_zyx: bool
    _position_offset: Vector
    _rotation_matrix: Matrix
    _rotation_matrix_inv: Matrix
    _output: any

    def __init__(
            self,
            start: int,
            end: int,
            anim_parameters: AnimParameters):

        self._start = start
        self._end = end
        self._anim_parameters = anim_parameters

    def _setup(self):
        self._is_quat = False
        self._obj_rotation_mode = 'XYZ'
        self._rotate_zyx = False
        self._position_offset = Vector()
        self._rotation_matrix = Matrix.Identity(4)
        self._rotation_matrix_inv = self._rotation_matrix.copy()
        self._output = SA3D_Modeling.KEYFRAMES()

    def _eval_nonlinear_frames(
            self,
            fcurve: FCurve,
            start: int,
            end: int,
            result: set[int]):

        frames = []
        values = {}
        for i in range(start, end+1):
            values[i] = fcurve.evaluate(i)
            frames.append(i)

        if self._anim_parameters.interpolation_threshold > 0:
            from ..utility.math_utils import remove_deviations
            remove_deviations(
                frames,
                values,
                None,
                None,
                self._anim_parameters.interpolation_threshold,
                lambda a, b, t: a * (1-t) + b * t,
                lambda a, b: abs(a - b))

        # removing the first and last frame
        result.update(frames)

    def _eval_export_frames(self, fcurve: FCurve):
        result = set()

        if fcurve is None or len(fcurve.keyframe_points) == 0:
            return result

        nonlinears = set()

        was_constant = False
        for kf in fcurve.keyframe_points:
            key_frame = kf.co.x
            key_left = math.floor(key_frame)
            key_right = math.ceil(key_frame)

            result.add(key_left)
            result.add(key_right)

            if was_constant and key_left == key_right:
                result.add(key_left - 1)
            was_constant = kf.interpolation == 'CONSTANT'

            if kf.interpolation not in ['LINEAR', 'CONSTANT']:
                nonlinears.add(key_right)

        tmp_list = list(result)
        tmp_list.sort()

        for nl_start in nonlinears:
            nl_start_index = tmp_list.index(nl_start)
            if nl_start_index == len(tmp_list) - 1:
                continue

            nl_end = tmp_list[nl_start_index + 1]

            if nl_start == nl_end - 1:
                continue

            self._eval_nonlinear_frames(
                fcurve,
                nl_start, nl_end,
                result)

        return result

    def _bake_keyframes(self, fcurves: list[FCurve], fallback: float = 0):
        frames = {self._start, self._end}
        for curve in fcurves:
            frames.update(self._eval_export_frames(curve))

        result: dict[int, list[float]] = {}
        for frame in sorted(frames):
            result[frame - self._start] = [
                (vc.evaluate(frame) if vc is not None else fallback)
                for vc in fcurves]

        return result

    def _evaluate_location(
            self,
            curves: list[FCurve],
            output,
            base_matrix: Matrix):

        pos_values = self._bake_keyframes(curves)

        for i, val in pos_values.items():
            position = Vector((val[0], val[1], val[2]))

            position = position @ self._rotation_matrix_inv
            position += self._position_offset

            position = base_matrix @ position

            net_position = System.VECTOR3(
                position.x,
                position.z,
                -position.y)

            output.Add(i, net_position)

    def _get_complementary_matrices(
            self,
            euler: Euler,
            previous_euler: Euler,
            base_rotation: Matrix):

        if previous_euler is None:
            return None

        difx = euler.x - previous_euler.x
        dify = euler.y - previous_euler.y
        difz = euler.z - previous_euler.z

        maxdif = max([abs(difx), abs(dify), abs(difz)])

        complementary_len = math.floor(maxdif / math.pi)
        if complementary_len == 0:
            return None

        # we produce one more to ensure no rounding errors
        complementary_len += 1

        # add one more, the last frame should not be our input euler
        dif_fac = 1.0 / (complementary_len + 1)

        result = []

        for i in range(complementary_len):
            compl_fac = dif_fac * (i + 1)

            compl_euler = Euler(
                (
                    previous_euler.x + compl_fac * difx,
                    previous_euler.y + compl_fac * dify,
                    previous_euler.z + compl_fac * difz,
                ),
                previous_euler.order
            )

            mtx = base_rotation @ (self._rotation_matrix @
                                   compl_euler.to_matrix().to_4x4())
            net_mtx = o_matrix.bpy_to_net_matrix(mtx)

            result.append(net_mtx)

        return result

    def _evaluate_rotation(
            self,
            rot_curves: list[FCurve],
            base_matrix: Matrix):
        rot_values = self._bake_keyframes(rot_curves)

        matrices = SA3D_Modeling.GEN_MATRIX_KEYFRAMES()
        compl_matrices = SA3D_Modeling.GEN_COMPLEMENTARY_MATRIX_DICT()
        base_rotation = base_matrix.to_quaternion().to_matrix().to_4x4()

        def add_rotation(index: int, mtx: Matrix):
            mtx = base_rotation @ (self._rotation_matrix @ mtx.to_4x4())
            net_mtx = o_matrix.bpy_to_net_matrix(mtx)
            matrices.Add(index, net_mtx)

        if self._is_quat:
            for i, val in rot_values.items():
                quaternion = Quaternion((val[0], val[1], val[2], val[3]))
                add_rotation(i, quaternion.to_matrix())
        else:
            previous_euler = None
            previous_frame = None
            rot_mode = self._obj_rotation_mode
            for i, val in rot_values.items():
                euler = Euler((val[0], val[1], val[2]), rot_mode)
                add_rotation(i, euler.to_matrix())

                complementary = self._get_complementary_matrices(
                    euler, previous_euler, base_rotation)

                if complementary is not None:
                    compl_matrices.Add(previous_frame, complementary)

                previous_euler = euler
                previous_frame = i

        if compl_matrices.Count == 0:
            compl_matrices = None

        if (self._anim_parameters.rotation_mode == 'QUATERNION'
                or self._anim_parameters.rotation_mode == 'KEEP'
                and self._is_quat):

            SA3D_Modeling.KEYFRAME_ROTATION_UTILS.MatrixToQuaternion(
                self._output,
                matrices,
                self._is_quat,
                self._anim_parameters.quaternion_threshold,
                self._rotate_zyx)
        else:
            SA3D_Modeling.KEYFRAME_ROTATION_UTILS.MatrixToEuler(
                self._output,
                matrices,
                self._is_quat,
                self._anim_parameters.quaternion_threshold,
                self._rotate_zyx,
                compl_matrices)

    def _evaluate_scale(
            self,
            scale_curves: list[FCurve],
            base_matrix: Matrix):
        base_scale = base_matrix.to_scale()
        scale_values = self._bake_keyframes(scale_curves)

        for i, val in scale_values.items():
            scale = Vector((val[0], val[1], val[2])) * base_scale
            net_scale = System.VECTOR3(scale[0], scale[2], scale[1])
            self._output.Scale.Add(i, net_scale)

    @staticmethod
    def all_none(iterator):
        return all(v is None for v in iterator)

    def _optimize_keyframes(self):

        if not (self._anim_parameters.general_optim_thresh > 0
                or self._anim_parameters.quaternion_optim_thresh > 0):
            return

        self._output.Optimize(
            self._anim_parameters.general_optim_thresh,
            self._anim_parameters.quaternion_optim_thresh,
            0,
            True)

    def _get_node_curves(
            self,
            fcurves: bpy.types.ActionFCurves,
            datapath_prefix: str):

        location_datapath = datapath_prefix + "location"
        rotation_datapath = datapath_prefix + "rotation_" + (
            "quaternion" if self._is_quat else "euler")
        scale_datapath = datapath_prefix + "scale"

        return [
            fcurves.find(location_datapath, index=0),
            fcurves.find(location_datapath, index=1),
            fcurves.find(location_datapath, index=2),

            fcurves.find(rotation_datapath, index=0),
            fcurves.find(rotation_datapath, index=1),
            fcurves.find(rotation_datapath, index=2),
            fcurves.find(rotation_datapath, index=3),

            fcurves.find(scale_datapath, index=0),
            fcurves.find(scale_datapath, index=1),
            fcurves.find(scale_datapath, index=2),
        ]

    def evaluate_node_keyframe_set(
            self,
            fcurves: bpy.types.ActionFCurves,
            datapath_prefix: str,
            base_matrix: Matrix,
            obj_rotation_mode: str,
            rotate_zyx: bool,
            position_offset: Vector,
            rotation_matrix: Matrix):

        self._setup()
        self._is_quat = obj_rotation_mode == 'QUATERNION'
        self._obj_rotation_mode = obj_rotation_mode
        self._rotate_zyx = rotate_zyx
        self._position_offset = position_offset
        self._rotation_matrix = rotation_matrix
        self._rotation_matrix_inv = rotation_matrix.inverted()

        curves = self._get_node_curves(fcurves, datapath_prefix)

        if self.all_none(curves):
            return None

        pos_curves = curves[0:3]
        if not self.all_none(pos_curves):
            self._evaluate_location(
                pos_curves, self._output.Position, base_matrix)

        rot_curves = curves[3:7]
        if not self.all_none(rot_curves):
            self._evaluate_rotation(rot_curves, base_matrix)

        scale_curves = curves[7:]
        if not self.all_none(scale_curves):
            self._evaluate_scale(scale_curves, base_matrix)

        self._optimize_keyframes()

        if self._anim_parameters.ensure_positive_euler_angles:
            SA3D_Modeling.KEYFRAME_ROTATION_UTILS.EnsurePositiveEulerRotationAngles(
                self._output, True)

        return self._output

    def _get_camera_curves(self, camera_actions: camera_utils.CameraActionSet):
        search = [
            (camera_actions.position, "location", 0),
            (camera_actions.position, "location", 1),
            (camera_actions.position, "location", 2),
            (camera_actions.target, "location", 0),
            (camera_actions.target, "location", 1),
            (camera_actions.target, "location", 2),
            (camera_actions.target, "rotation_euler", 2),
            (camera_actions.fov, "lens", None)
        ]

        result = []
        for action, name, index in search:
            if action is None:
                result.append(None)
            elif index is None:
                result.append(action.fcurves.find(name))
            else:
                result.append(action.fcurves.find(name, index=index))

        return result

    def evaluate_camera_keyframe_set(
            self,
            camera_setup: camera_utils.CameraSetup,
            camera_actions: camera_utils.CameraActionSet):

        self._setup()
        base_matrix = camera_setup.container.matrix_world
        curves = self._get_camera_curves(camera_actions)

        if self.all_none(curves):
            return None

        end_frame = self._end - self._start

        def bakeable(curves, output, default_value):
            if not self.all_none(curves):
                return True

            output.Add(0, default_value)
            output.Add(end_frame, default_value)
            return False

        def evaluate_positions(curves, output, default_location):
            vector = System.VECTOR3(
                default_location.x,
                default_location.z,
                -default_location.y)

            if bakeable(curves, output, vector):
                self._evaluate_location(curves, output, base_matrix)

        evaluate_positions(
            curves[0:3],
            self._output.Position,
            camera_setup.camera.location)

        evaluate_positions(
            curves[3:6],
            self._output.Target,
            camera_setup.target.location)

        roll_curve = [curves[6]]
        if bakeable(
                roll_curve,
                self._output.Roll,
                camera_setup.target.rotation_euler.z):

            roll_values = self._bake_keyframes(roll_curve)
            for i, val in roll_values.items():
                self._output.Roll.Add(i, -val[0])

        fov_curve = [curves[7]]
        if bakeable(
                fov_curve,
                self._output.Angle,
                camera_setup.camera_data.angle):

            fov_values = self._bake_keyframes(fov_curve)
            sensor_width = camera_setup.camera_data.sensor_width

            for i, val in fov_values.items():
                angle = 2 * math.atan(sensor_width / (2 * val[0]))
                self._output.Angle.Add(i, angle)

        self._optimize_keyframes()
        return self._output


class ShapeKeyframeEvaluator:

    _modelmesh: ModelMesh
    _normal_mode: str

    _shape_dict: dict[str, tuple[any, any]]

    _depsgraph: bpy.types.Depsgraph
    _duration: int
    _start: int
    _frames: int

    def __init__(self, modelmesh: ModelMesh, normal_mode: str):
        self._modelmesh = modelmesh
        self._normal_mode = normal_mode

        self._shape_dict = {}

        self._depsgraph = None
        self._duration = 0
        self._start = 0
        self._frames = 0

    def _verify_keyframe(
            self,
            keyframe: bpy.types.Keyframe,
            action_name: str,
            shape_name: str):

        if keyframe.co[0] != int(keyframe.co[0]):
            raise UserException(
                f"One or more keys in shape animation {shape_name}"
                f" (action {action_name}) are NOT aligned with the"
                " frame number")

        elif keyframe.co[1] not in [0.0, 1.0]:
            raise UserException((
                f"One or more keys in shape animation {shape_name}"
                f" (action {action_name}) are NOT 0.0 or 1.0"))

    def _evaluate_curves(self, action: Action):

        last_frame = None

        curves: list[tuple[FCurve, str]] = []
        for fcurve in action.fcurves:
            if not (fcurve.data_path.startswith("key_blocks[\"")
                    and fcurve.data_path.endswith("\"].value")):
                continue

            shape_name = fcurve.data_path[12:-8]
            curves.append((fcurve, shape_name))

            curve_end = fcurve.keyframe_points[-1].co[0]
            if last_frame is None:
                last_frame = curve_end
            else:
                last_frame = max(last_frame, curve_end)

        last_frame = int(last_frame) - self._start
        frames: dict[int, str] = {}
        frame_map = [False] * (last_frame + 1)

        def mark_frame(mark_frame):
            if frame_map[mark_frame]:
                raise UserException(
                    f"One or more shapes in action {action.name}"
                    f" overlap at frame {mark_frame}")
            frame_map[mark_frame] = True

        for fcurve, shape_name in curves:
            previous_frame = None
            previous_state = None

            for point in fcurve.keyframe_points:
                self._verify_keyframe(point, action.name, shape_name)

                frame = int(point.co[0]) - self._start
                state = point.co[1] == 1.0

                if state:
                    frames[frame] = shape_name
                    mark_frame(frame)
                elif frame not in frames:
                    frames[frame] = None

                if previous_frame is None:
                    previous_frame = 0
                    previous_state = state
                    if frame > 0 and state:
                        frames[0] = shape_name
                        mark_frame(0)

                if frame > (previous_frame + 1) and state and previous_state:
                    for i in range(previous_frame + 1, frame):
                        mark_frame(i)

                previous_frame = frame
                previous_state = state

            if (previous_frame is not None
                    and previous_frame < last_frame
                    and previous_state):

                frames[last_frame] = shape_name
                mark_frame(last_frame)

                if last_frame > (previous_frame + 1):
                    for i in range(previous_frame + 1, last_frame):
                        mark_frame(i)

        return frames

    def _evaluate_keyframes(self, action: Action):

        frames = self._evaluate_curves(action)

        if len(frames) == 0 or all(v is None for v in frames.values()):
            return None

        return frames

    def _create_vertex_array(
            self,
            shape_name: str,
            mesh: bpy.types.Mesh,
            matrix: Matrix, ):

        def get_position(vertex):
            position = matrix @ vertex.co
            return System.VECTOR3(
                position.x,
                position.z,
                -position.y,
            )

        if self._modelmesh.vertex_mapping is not None:
            shape_positions = [
                get_position(mesh.vertices[vertex_index])
                for vertex_index in self._modelmesh.vertex_mapping]
        else:
            shape_positions = [get_position(vertex)
                               for vertex in mesh.vertices]

        return SA3D_Common.LABELED_ARRAY[System.VECTOR3](
            shape_name.lower(), shape_positions)

    def _create_normal_array(
            self,
            shape_name: str,
            mesh: bpy.types.Mesh,
            matrix: Matrix):

        if self._normal_mode not in ['NULLED', 'FULL']:
            return None

        if self._normal_mode == 'NULLED':
            shape_normals = [System.VECTOR3(0, 0, 0)]
        else:  # 'FULL'
            normals = ModelMesh.get_normals(mesh)

            def get_normal(normal):
                normal = matrix @ normal
                return System.VECTOR3(
                    normal.x,
                    normal.z,
                    -normal.y,
                )

            if self._modelmesh.vertex_mapping is not None:
                shape_normals = [
                    get_normal(normals[vertex_index])
                    for vertex_index in self._modelmesh.vertex_mapping]
            else:
                shape_normals = [get_normal(normal) for normal in normals]

        normal_name = (
            shape_name
            .lower()
            .replace("vtx", "nrm")
            .replace("vertex", "normal")
            .replace("vert", "norm")
        )

        if normal_name == shape_name.lower():
            normal_name += "_normal"

        return SA3D_Common.LABELED_ARRAY[System.VECTOR3](
            normal_name, shape_normals)

    def _create_keyframes(self):

        keyframes = SA3D_Modeling.KEYFRAMES()

        ref_name = self._modelmesh.object.data.shape_keys.reference_key.name
        vertex_matrix, normal_matrix = self._modelmesh.get_matrices()

        for frame, shape_name in self._frames.items():
            if shape_name is None:
                shape_name = ref_name

            if shape_name not in self._shape_dict:
                shape_mesh = self._modelmesh.get_shape_model(
                    shape_name, self._depsgraph)

                vertex_array = self._create_vertex_array(
                    shape_name,
                    shape_mesh,
                    vertex_matrix
                )

                normal_array = self._create_normal_array(
                    shape_name,
                    shape_mesh,
                    normal_matrix
                )

                self._shape_dict[shape_name] = (vertex_array, normal_array)
            else:
                vertex_array, normal_array = self._shape_dict[shape_name]

            keyframes.Vertex.Add(frame, vertex_array)
            if normal_array is not None:
                keyframes.Normal.Add(frame, normal_array)

        return keyframes

    def evaluate(
            self,
            action: Action,
            depsgraph: bpy.types.Depsgraph,
            start: int,
            duration: int):

        self._depsgraph = depsgraph
        self._duration = duration
        self._start = start

        self._frames = self._evaluate_keyframes(action)
        keyframes = self._create_keyframes()

        return keyframes
