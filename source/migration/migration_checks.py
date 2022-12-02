import bpy


def is_old_addon_enabled(context: bpy.types.Context):
    for addon in context.preferences.addons:
        if addon.module.startswith("BlenderSASupport"):
            return True
    return False


def check_file_contains_old_data():
    for scene in bpy.data.scenes:
        if "saSettings" in scene:
            return True

    for object in bpy.data.objects:
        if "saSettings" in object or "saObjflags" in object:
            return True

        if object.type == 'ARMATURE':
            for bone in object.data.bones:
                if "saObjflags" in bone:
                    return True

    for mesh in bpy.data.meshes:
        if "saSettings" in mesh:
            return True

    for material in bpy.data.materials:
        if "saSettings" in material:
            return True

    return False


def update_checks():
    saio = bpy.data.scenes[0].saio_scene
    saio.found_migrate_data = check_file_contains_old_data()

    if not saio.checked_for_migrate_data:
        saio.checked_for_migrate_data = True
