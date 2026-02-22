import bpy
from ..utility import camera_utils
from ..exporting.o_motion import ActionSet
from ..exceptions import UserException

ACTION_POSTFIX = ["_position", "_target", "_fov"]

def _update_object(obj: bpy.types.Object):
	evententry_properties = obj.saio_event_entry

	def flag_migrate(old: str, new: str):
		if old in evententry_properties:
			evententry_properties[new] = evententry_properties[old]

	flag_migrate("unk0", "has_environment")
	flag_migrate("enable_lighting", "no_fog_and_easy_draw")
	flag_migrate("unk2", "light1")
	flag_migrate("disable_shadow_catching", "light2")
	flag_migrate("unk4", "light3")
	flag_migrate("unk5", "light4")
	flag_migrate("unk6", "modifier_volume")
	flag_migrate("unk9", "use_simple")

def update_file():
	for obj in bpy.data.objects:
		_update_object(obj)

def _get_slot(action: bpy.types.Action, id_type: str):
	found = False
	for slot in action.slots:
		if slot.target_id_type == id_type:
			found = True
	
	if found == False:
		raise UserException(
			f"Invalid action type! The action \"{action.name}\" does"
			f" not have a slot for id type \"{id_type}\"!"
		)
	
	return slot

def _replace_idd_action(
		idd: bpy.types.ID, 
		action: bpy.types.Action, 
		slot: bpy.types.ActionSlot, 
		new_action: bpy.types.Action, 
		new_slot: bpy.types.ActionSlot):
	
	src_channelbag = action.layers[0].strips[0].channelbag(slot)
	dst_channelbag = new_action.layers[0].strips[0].channelbag(new_slot, ensure=True)
	for fcurve in src_channelbag.fcurves:
		dst_channelbag.fcurves.new_from_fcurve(fcurve)

	anim_data: bpy.types.AnimData = idd.animation_data
		
	if anim_data.action == action and anim_data.action_slot == slot:
		anim_data.action = new_action
		anim_data.action_slot = new_slot

	for track in anim_data.nla_tracks:
		for strip in track.strips:
			if strip.action == action and strip.action_slot == slot:
				strip.action = new_action
				strip.action_slot = new_slot

def get_old_camera_action_setup(camera_setup: camera_utils.CameraSetup, frame: int):
	if camera_setup is None:
		return None

	# priority row: position -> target+roll -> fov
	id_data: list[bpy.types.ID] = (
		camera_setup.camera,
		camera_setup.target,
		camera_setup.camera_data
	)

	action = None
	postfix = None
	for idd, postfix in zip(id_data, ACTION_POSTFIX):
		action = ActionSet.from_data(idd, frame)
		if action is not None:
			break

	if action is None:
		return None

	if not action.name.endswith(postfix):
		raise UserException(
			f"Action \"{action.name}\" is a {postfix[1:]} action and it's"
			f" name has to end with \"{postfix}\" to be recognized as"
			" such, otherwise the other actions cannot be found!")

	name = action.name[:-len(postfix)]

	actions = []
	for idd, postfix in zip(id_data, ACTION_POSTFIX):
		index = bpy.data.actions.find(name + postfix)
		if index == -1:
			actions.append(None)
		else:
			action = bpy.data.actions[index]
			slot = _get_slot(action, idd.id_type)
			actions.append(ActionSet(action, slot))

	return actions

def merge_old_camera_actions(camera_setup: camera_utils.CameraSetup | None, camera_actions: list[ActionSet | None] | None):
	if camera_setup is None or camera_actions is None:
		return
	
	for action, postfix in zip(camera_actions, ACTION_POSTFIX):
		if action is None:
			continue
		name = action.name[:-len(postfix)]

	new_action = camera_utils.CameraAction.create_set(name)

	id_data: list[bpy.types.ID] = (
		camera_setup.camera,
		camera_setup.target,
		camera_setup.camera_data
	)

	channelbags = [
		new_action.position_channelbag,
		new_action.target_channelbag,
		new_action.fov_channelbag,
	]

	for idd, channelbag, action in zip(id_data, channelbags, camera_actions):
		if action is None:
			continue

		_replace_idd_action(
			idd,
			action.action,
			action.slot,
			new_action.action,
			channelbag.slot
		)

class OldShapeActionCollection:

    actions: dict[bpy.types.Object, ActionSet]
    motion_name: str

    def __init__(self):
        self.actions = {}
        self.motion_name = ""

class OldShapeActionCollector:

    target: bpy.types.Object
    frame: int

    starter_action: ActionSet

    result: OldShapeActionCollection

    def __init__(
            self,
            target: bpy.types.Object,
            frame: int):

        self.target = target
        self.frame = frame
        self.starter_action = None
        self.result = None

        if target.type == 'ARMATURE':
            from ..exporting.o_shapemotion import check_is_shape_motion_viable
            check_is_shape_motion_viable(target)

    def _setup(self):
        self.starter_action = None
        self.result = OldShapeActionCollection()

    def _should_be_skipped(self, obj: bpy.types.Object):
        from ..utility.general import get_armature_modifier
        return (
            obj.type != 'MESH'
            or obj.data.shape_keys is None
            or get_armature_modifier(obj) is not None
        )

    def _find_starter_action(self, model: bpy.types.Object) -> ActionSet | None:
        if self._should_be_skipped(model):
            return None

        action = ActionSet.from_data(
            model.data.shape_keys,
            self.frame,
            ignore_selected=False
        )

        if action is None:
            return None

        elif not action.name.endswith("_" + model.name):
            raise UserException(
                f"Target Action \"{action.name}\" of object"
                f" \"{model.name}\" does not match naming!\n"
                "Has to end with objectname\n"
                f"(e.g. \"ExampleActionName_{model.name}\")")

        return action

    def _find_armature_starter_action(self):
        for child in self.target.children:
            action = self._find_starter_action(child)

            if action is not None:
                self.starter_action = action
                self.result.motion_name = action.name[:-(1 + len(child.name))]
                return

    def _collect_armature(self):
        self._find_armature_starter_action()

        if self.starter_action is None:
            return

        for child in self.target.children:
            if child.parent_type != 'BONE' or self._should_be_skipped(child):
                continue

            try:
                action = bpy.data.actions[
                    f"{self.result.motion_name}_{child.name}"]
            except KeyError:
                continue

            slot = _get_slot(action, "KEY")
            self.result.actions[child] = ActionSet(action, slot)

    def _collect_object(self):
        action = self._find_starter_action(self.target)
        if action is not None:
            self.result.actions[self.target] = action
            self.result.motion_name = action.name

    def collect(self):
        self._setup()

        if self.target.type == 'ARMATURE':
            self._collect_armature()
        else:
            self._collect_object()

        if len(self.result.actions) == 0:
            return None

        return self.result

    @staticmethod
    def collect_shape_actions(target: bpy.types.Object, frame: int):
        collector = OldShapeActionCollector(target, frame)
        return collector.collect()

def merge_old_shape_actions(actions: OldShapeActionCollection):
	
	new_action = bpy.data.actions.new(actions.motion_name)
	layer = new_action.layers.new("Layer")
	layer.strips.new(type="KEYFRAME")

	for object, action in actions.actions.items():
		dst_slot = new_action.slots.new("KEY", object.name)

		_replace_idd_action(
			object.data.shape_keys,
			action.action,
			action.slot,
			new_action,
			dst_slot
		)
		