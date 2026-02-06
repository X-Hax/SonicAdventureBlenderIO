import bpy

SLOT_DEF = {
    "Position" : "OBJECT", 
    "Target" : "OBJECT", 
    "Fov" : "CAMERA"
}


class CameraSetup:

    container: bpy.types.Object
    '''Parent of the camera and target objects. Serves no other purpose than
      grouping the camera and target into one hierarchy'''

    camera: bpy.types.Object
    '''Camera object'''

    target: bpy.types.Object
    '''Object at which the camera looks and which depicts roll'''

    def __init__(
            self,
            container: bpy.types.Object,
            camera: bpy.types.Object,
            target: bpy.types.Object):

        self.container = container
        self.camera = camera
        self.target = target

    @staticmethod
    def _get_setup(obj: bpy.types.Object) -> 'CameraSetup':
        if (obj is None
                or obj.type != 'EMPTY'
                or len(obj.children) != 2):
            return None

        camera = obj.children[0]
        target = obj.children[1]

        if camera.type != 'CAMERA':
            t = target
            target = camera
            camera = t

        if camera.type != 'CAMERA' or target.type != 'EMPTY':
            return None

        return CameraSetup(obj, camera, target)

    @staticmethod
    def get_setup(obj: bpy.types.Object):
        if obj is not None:
            if obj.parent is None:
                return CameraSetup._get_setup(obj)
            elif obj.parent.parent is None:
                return CameraSetup._get_setup(obj.parent)
        return None

    @staticmethod
    def create_setup(
            name: str,
            collection: bpy.types.Collection,
            create_nla_tracks: bool):

        camera_controller = bpy.data.objects.new(
            name + "_camera_controller", None)
        camera_controller.saio_event_entry.entry_type = 'NONE'
        camera_controller.empty_display_type = 'CUBE'
        camera_controller.empty_display_size = 0.2

        camera = bpy.data.cameras.new(name)
        camera.animation_data_create()

        camera_object = bpy.data.objects.new(name + "_camera", camera)
        camera_object.animation_data_create()
        camera_object.parent = camera_controller

        camera_target = bpy.data.objects.new(name + "_camera_target", None)
        camera_target.parent = camera_controller
        camera_target.animation_data_create()

        if create_nla_tracks:
            camera.animation_data.nla_tracks.new()
            camera_object.animation_data.nla_tracks.new()
            camera_target.animation_data.nla_tracks.new()

        result = (camera_controller, camera_object, camera_target)

        for obj in result:
            collection.objects.link(obj)

        track_to: bpy.types.TrackToConstraint \
            = camera_object.constraints.new("TRACK_TO")
        track_to.target = camera_target

        transform: bpy.types.TransformConstraint \
            = camera_object.constraints.new("TRANSFORM")
        transform.target = camera_target
        transform.use_motion_extrapolate = True
        transform.target_space = 'LOCAL'
        transform.owner_space = 'LOCAL'
        transform.map_from = 'ROTATION'
        transform.from_max_z_rot = 1
        transform.map_to = 'ROTATION'
        transform.to_max_z_rot = 1
        transform.mix_mode_rot = 'AFTER'

        return CameraSetup(camera_controller, camera_object, camera_target)

    @property
    def camera_data(self) -> bpy.types.Camera:
        return self.camera.data


class CameraAction:

    action: bpy.types.Action
    position: bpy.types.ActionSlot | None
    target: bpy.types.ActionSlot | None
    fov: bpy.types.ActionSlot | None

    @property
    def position_channelbag(self):
        return self._get_channelbag(self.position)

    @property
    def target_channelbag(self):
        return self._get_channelbag(self.target)
    
    @property
    def fov_channelbag(self):
        return self._get_channelbag(self.fov)

    def __init__(
            self,
            action: bpy.types.Action,
            position: bpy.types.ActionSlot | None,
            target: bpy.types.ActionSlot | None,
            fov: bpy.types.ActionSlot | None):

        self.action = action
        self.position = position
        self.target = target
        self.fov = fov

    def _get_channelbag(self, slot: bpy.types.ActionSlot | None):
        if slot is None:
            return None
        
        layer = self.action.layers[0]
        strip: bpy.types.ActionKeyframeStrip = layer.strips[0]
        return strip.channelbag(slot)

    def as_list(self):
        return [self.position, self.target, self.fov]

    @staticmethod
    def create_set(name: str):

        action = bpy.data.actions.new(name)
        slot_names = list(SLOT_DEF.keys())
        slot_types = list(SLOT_DEF.values())

        position = action.slots.new(slot_types[0], slot_names[0])
        target = action.slots.new(slot_types[1], slot_names[1])
        fov = action.slots.new(slot_types[2], slot_names[2])

        layer = action.layers.new("Layer")
        strip: bpy.types.ActionKeyframeStrip = layer.strips.new(type="KEYFRAME")

        strip.channelbags.new(position)
        strip.channelbags.new(target)
        strip.channelbags.new(fov)

        return CameraAction(action, position, target, fov)
