import bpy

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