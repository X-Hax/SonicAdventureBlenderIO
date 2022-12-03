import os
import bpy


def get_path():
    return os.path.dirname(os.path.realpath(__file__))


def get_name():
    return os.path.basename(get_path())


def get_prefs():
    return bpy.context.preferences.addons[get_name()].preferences


def is_landtable(context: bpy.types.Context):
    if context is None:
        context = bpy.context
    return context.scene.saio_scene.scene_is_level


def is_land_entry(context: bpy.types.Context):
    if context is None:
        context = bpy.context
    return (
        context.active_object is not None
        and context.active_object.type == 'MESH'
    )


def get_active_node_properties(context: bpy.types.Context):
    if context is None:
        context = bpy.context

    obj = context.active_object

    if (obj is None
            or obj.type not in ['MESH', 'ARMATURE', 'EMPTY']):
        return None

    if obj.type == "ARMATURE":
        if obj.mode == "POSE":
            obj = obj.data.bones.active
        elif obj.mode == "EDIT":
            obj = obj.data.edit_bones.active

    if obj is None:
        return None
    return (obj.name, obj.saio_node)
