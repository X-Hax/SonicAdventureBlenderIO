
class AnimParameters:

    bone_localspace: bool
    rotation_mode: str
    interpolation_threshold: float
    quaternion_threshold: float
    general_optim_thresh: float
    quaternion_optim_thresh: float
    short_rot: bool
    ensure_positive_euler_angles: bool

    def __init__(
            self,
            bone_localspace: bool,
            rotation_mode: str,
            interpolation_threshold: float,
            quaternion_threshold: float,
            general_optim_thresh: float,
            quaternion_optim_thresh: float,
            short_rot: bool = False,
            ensure_positive_euler_angles: bool = True):

        self.bone_localspace = bone_localspace
        self.rotation_mode = rotation_mode
        self.interpolation_threshold = interpolation_threshold
        self.quaternion_threshold = quaternion_threshold
        self.general_optim_thresh = general_optim_thresh
        self.quaternion_optim_thresh = quaternion_optim_thresh
        self.short_rot = short_rot
        self.ensure_positive_euler_angles = ensure_positive_euler_angles
