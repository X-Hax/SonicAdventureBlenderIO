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

			found = False
			for slot in action.slots:
				if slot.target_id_type == idd.id_type:
					found = True
			
			if found == False:
				raise UserException(
					f"Invalid action type! The action \"{action.name}\" does"
					f" not have a slot for id type \"{idd.id_type}\"!"
				)

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

		src_channelbag = action.channelbag
		for fcurve in src_channelbag.fcurves:
			channelbag.fcurves.new_from_fcurve(fcurve)
		
		anim_data: bpy.types.AnimData = idd.animation_data
		
		if anim_data.action == action.action and anim_data.action_slot == action.slot:
			anim_data.action = new_action.action
			anim_data.action_slot = channelbag.slot

		for track in anim_data.nla_tracks:
			for strip in track.strips:
				if strip.action == action.action and strip.action_slot == action.slot:
					strip.action = new_action.action
					strip.action_slot = channelbag.slot