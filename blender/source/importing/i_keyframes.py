import bpy
from mathutils import Vector, Matrix, Euler

from . import i_matrix

from ..dotnet import SA3D_Modeling
from ..exceptions import SAIOException


class TransformKeyframeProcessor:

    action: bpy.types.Action
    '''Output action'''

    group: str
    '''FCurve group'''

    path_prefix: str
    '''FCurve path prefix'''

    rotation_mode: str
    '''How the rotation mode should be handled'''

    rotate_zyx: bool
    '''Whether to rotate in ZYX order'''

    quaternion_conversion_deviation: float
    '''quaternion <-> euler interpolation deviation'''

    def __init__(
            self,
            action: bpy.types.Action = None,
            group: str = "",
            path_prefix: str = "",
            rotation_mode: str = "KEEP",
            rotate_zyx: bool = False,
            quaternion_conversion_deviation: float = 0.05):

        self.action = action
        self.group = group
        self.path_prefix = path_prefix
        self.rotation_mode = rotation_mode
        self.rotate_zyx = rotate_zyx
        self.quaternion_conversion_deviation = quaternion_conversion_deviation

        if rotation_mode not in ["ANIM", "KEEP"]:
            raise SAIOException("Rotation mode invalid!")

    def _create_keyframe_points(self, name: str, index: int):
        '''Creates a new fcurve on the action and
        returns its keyframe points collection'''

        return self.action.fcurves.new(
            self.path_prefix + name,
            index=index,
            action_group=self.group).keyframe_points

    def process_position_keyframes(
            self,
            keyframes,
            offset: Vector | None = None,
            rotation_matrix: Matrix | None = None):

        if keyframes.Count == 0:
            return

        if offset is None:
            offset = Vector()

        if rotation_matrix is None:
            rotation_matrix = Matrix.Identity(4)
        else:
            rotation_matrix = rotation_matrix.inverted()

        location_x = self._create_keyframe_points("location", 0)
        location_y = self._create_keyframe_points("location", 1)
        location_z = self._create_keyframe_points("location", 2)

        for kf_pos in keyframes:

            position = Vector((
                kf_pos.Value.X,
                -kf_pos.Value.Z,
                kf_pos.Value.Y))
            position -= offset
            position = position @ rotation_matrix

            location_x.insert(kf_pos.Key, position.x).interpolation = 'LINEAR'
            location_y.insert(kf_pos.Key, position.y).interpolation = 'LINEAR'
            location_z.insert(kf_pos.Key, position.z).interpolation = 'LINEAR'

    def process_scale_keyframes(
            self,
            keyframes):

        if keyframes.Count == 0:
            return

        scale_x = self._create_keyframe_points("scale", 0)
        scale_y = self._create_keyframe_points("scale", 1)
        scale_z = self._create_keyframe_points("scale", 2)

        for kf_scale in keyframes:
            scale = kf_scale.Value
            scale_x.insert(kf_scale.Key, scale.X).interpolation = 'LINEAR'
            scale_y.insert(kf_scale.Key, scale.Z).interpolation = 'LINEAR'
            scale_z.insert(kf_scale.Key, scale.Y).interpolation = 'LINEAR'

    #########################################################

    def _determine_rotation_mode(self, keyframe_set, default: str):
        if self.rotation_mode == 'KEEP':
            return default
        elif keyframe_set.EulerRotation.Count == 0:
            return 'QUATERNION'
        else:
            return 'XYZ'

    def _get_rotation_matrices(
            self,
            keyframe_set,
            rotation_matrix: Matrix,
            use_quaternion: bool):

        matrix_keyframes, converted, complementary = \
            SA3D_Modeling.KEYFRAME_ROTATION_UTILS.GetRotationMatrices(
                keyframe_set,
                use_quaternion,
                0,
                self.rotate_zyx,
                False,
                None)

        bmatrix_keyframes: dict[int, Matrix] = {}

        for kf_mtx in matrix_keyframes:
            mtx = i_matrix.net_to_bpy_matrix(kf_mtx.Value)
            bmatrix_keyframes[kf_mtx.Key] = rotation_matrix @ mtx

        bmatrix_complementary: dict[int, list[Matrix]] | None = None
        if complementary is not None:
            bmatrix_complementary = {}
            for kv in complementary:
                matrices = []
                for net_mtx in kv.Value:
                    mtx = i_matrix.net_to_bpy_matrix(net_mtx)
                    matrices.append(rotation_matrix @ mtx)
                bmatrix_complementary[kv.Key] = matrices

        return bmatrix_keyframes, bmatrix_complementary, converted

    def _process_euler_rotation_keyframes(
            self,
            matrix_keyframes: dict[int, Matrix],
            unconverted_frames: list[int] | None,
            complementary: dict[int, list[Matrix]],
            out_rotation_mode: str):

        frames = []
        values = {}

        euler = Euler((0, 0, 0), out_rotation_mode)
        for frame, mtx in matrix_keyframes.items():
            euler = mtx.to_euler(out_rotation_mode, euler)

            frames.append(frame)
            values[frame] = euler.copy()

            if complementary is not None and frame in complementary:
                for mtx in complementary[frame]:
                    euler = mtx.to_euler(out_rotation_mode, euler)

        if (unconverted_frames is not None
                and self.quaternion_conversion_deviation > 0):
            from ..utility.math_utils import (
                remove_deviations,
                lerp_euler,
                calc_euler_deviation
            )

            previous = None
            for i in unconverted_frames:
                if previous is not None:
                    remove_deviations(
                        frames,
                        values,
                        previous,
                        i,
                        self.quaternion_conversion_deviation,
                        lerp_euler,
                        calc_euler_deviation
                    )

                previous = i

        rotation_x = self._create_keyframe_points("rotation_euler", 0)
        rotation_y = self._create_keyframe_points("rotation_euler", 1)
        rotation_z = self._create_keyframe_points("rotation_euler", 2)

        for frame in frames:
            euler = values[frame]

            rotation_x.insert(frame, euler.x).interpolation = 'LINEAR'
            rotation_y.insert(frame, euler.y).interpolation = 'LINEAR'
            rotation_z.insert(frame, euler.z).interpolation = 'LINEAR'

    def _process_quaternion_rotation_keyframes(
            self,
            matrix_keyframes: dict[int, Matrix],
            unconverted_frames: list[int] | None):

        frames = []
        values = {}

        for frame, mtx in matrix_keyframes.items():
            frames.append(frame)
            values[frame] = mtx.to_quaternion()

        if (unconverted_frames is not None
                and self.quaternion_conversion_deviation > 0):
            from ..utility.math_utils import (
                remove_deviations,
                lerp_quaternion,
                calc_quaternion_deviation
            )

            previous = None
            for i in unconverted_frames:
                if previous is not None:
                    remove_deviations(
                        frames,
                        values,
                        previous,
                        i,
                        self.quaternion_conversion_deviation,
                        lerp_quaternion,
                        calc_quaternion_deviation
                    )

                previous = i

        rotation_w = self._create_keyframe_points("rotation_quaternion", 0)
        rotation_x = self._create_keyframe_points("rotation_quaternion", 1)
        rotation_y = self._create_keyframe_points("rotation_quaternion", 2)
        rotation_z = self._create_keyframe_points("rotation_quaternion", 3)

        for frame in frames:
            quaternion = values[frame]

            rotation_w.insert(frame, quaternion.w).interpolation = 'LINEAR'
            rotation_x.insert(frame, quaternion.x).interpolation = 'LINEAR'
            rotation_y.insert(frame, quaternion.y).interpolation = 'LINEAR'
            rotation_z.insert(frame, quaternion.z).interpolation = 'LINEAR'

    def process_rotation_keyframes(
            self,
            keyframe_set,
            out_rotation_mode: str,
            rotation_matrix: Matrix | None = None) -> str:

        if (keyframe_set.EulerRotation.Count > 0
                or keyframe_set.QuaternionRotation.Count > 0):

            if rotation_matrix is None:
                rotation_matrix = Matrix.Identity(4)

            out_rotation_mode = self._determine_rotation_mode(
                keyframe_set, out_rotation_mode)

            matrix_keyframes, complementary, converted = \
                self._get_rotation_matrices(
                    keyframe_set,
                    rotation_matrix,
                    out_rotation_mode == 'QUATERNION')

            unconverted_frames = None
            if converted:
                if out_rotation_mode == 'QUATERNION':
                    unconverted_frames = [
                        x.Key for x in keyframe_set.EulerRotation]
                else:
                    unconverted_frames = [
                        x.Key for x in keyframe_set.QuaternionRotation]

            if out_rotation_mode == 'QUATERNION':
                self._process_quaternion_rotation_keyframes(
                    matrix_keyframes, unconverted_frames)
            else:
                self._process_euler_rotation_keyframes(
                    matrix_keyframes,
                    unconverted_frames,
                    complementary,
                    out_rotation_mode)

        return out_rotation_mode

    #########################################################

    def process_transform_keyframes(
            self,
            keyframe_set,
            out_rotation_mode: str,
            position_offset: Vector | None = None,
            rotation_matrix: Matrix | None = None):

        if position_offset is None:
            position_offset = Vector()

        if rotation_matrix is None:
            rotation_matrix = Matrix.Identity(4)

        self.process_position_keyframes(
            keyframe_set.Position,
            position_offset,
            rotation_matrix
        )

        out_rotation_mode = self.process_rotation_keyframes(
            keyframe_set,
            out_rotation_mode,
            rotation_matrix
        )

        self.process_scale_keyframes(
            keyframe_set.Scale
        )

        return out_rotation_mode


class ShapeKeyframeProcessor:

    _object: bpy.types.Object
    '''Object with the mesh data'''

    _optimize: bool

    shape_mapping: dict[any, bpy.types.ShapeKey]
    '''Mapping .NET vector arrays to shape keys for reuse'''

    def __init__(self, obj: bpy.types.Object, optimize: bool):
        self._object = obj
        self._optimize = optimize
        self.shape_mapping = {}

        if self._object.type != "MESH":
            raise SAIOException("Object doesnt support shape motions!")

        if self._key is None:
            self._object.shape_key_add(name="basis")

    @property
    def _key(self) -> bpy.types.Key:
        return self._object.data.shape_keys

    def _verify(self, keyframe_set):
        if keyframe_set.Vertex.Count == 0:
            raise SAIOException("Motion import failure!")

    def _find_matching_shapekey(self, verts: list[Vector]):
        for shape_key in self._key.key_blocks:
            if (shape_key == self._key.reference_key
                    or shape_key in self.shape_mapping.values()):
                continue

            found = True
            for vert, svert in zip(verts, shape_key.data):
                if (vert - svert.co).length > 0.01:
                    found = False
                    break

            if found:
                return shape_key

        return None

    def _get_shapekey(
            self,
            vectors) -> bpy.types.ShapeKey:

        if vectors in self.shape_mapping:
            return self.shape_mapping[vectors]

        verts = []

        if vectors.Length > len(self._object.data.vertices):
            print(
                f"Warning: {self._object.name} has"
                " less vertices than shape anim!")
        elif vectors.Length < len(self._object.data.vertices):
            print(
                f"Warning: {self._object.name} has"
                " more vertices than shape anim!")

        vert_count = min(vectors.Length, len(self._object.data.vertices))
        for i in range(vert_count):
            co = vectors[i]
            verts.append(Vector((co.X, -co.Z, co.Y)))

        shape_key = None

        if self._optimize:
            shape_key = self._find_matching_shapekey(verts)

        if shape_key is None:
            shape_key = self._object.shape_key_add(
                name=vectors.Label, from_mix=False)

            for vert, svert in zip(verts, shape_key.data):
                svert.co = vert

        self.shape_mapping[vectors] = shape_key
        return shape_key

    def _get_curve(
            self,
            shape: bpy.types.ShapeKey,
            action: bpy.types.Action):

        if shape == self._key.reference_key:
            return None

        data_path = f"key_blocks[\"{shape.name}\"].value"
        curve = action.fcurves.find(data_path)
        if curve is None:
            curve = action.fcurves.new(data_path)

        return curve.keyframe_points

    def process(
            self,
            keyframe_set,
            output_action: bpy.types.Action,
            last_frame_number: int):

        self._verify(keyframe_set)

        previous: bpy.types.FCurveKeyframePoints = None
        previous_frame = None

        curves: set[bpy.types.FCurveKeyframePoints] = set()

        for kf in keyframe_set.Vertex:
            shape_key = self._get_shapekey(kf.Value)
            curve = self._get_curve(shape_key, output_action)

            if curve is not None:
                curves.add(curve)
                curve.insert(kf.Key, 1).interpolation = "LINEAR"

            if previous is not None and curve != previous:
                previous.insert(kf.Key, 0).interpolation = "LINEAR"
                if curve is not None:
                    curve.insert(previous_frame, 0).interpolation = "LINEAR"

            previous = curve
            previous_frame = kf.Key

        for curve in curves:
            if curve[0].co.x != 0:
                curve.insert(0, 0).interpolation = "LINEAR"

            last_frame = max(
                last_frame_number,
                kf.Key)  # pylint: disable=undefined-loop-variable

            if curve[-1].co.x != last_frame:
                curve.insert(last_frame, curve[-1].co.y
                             ).interpolation = "LINEAR"
