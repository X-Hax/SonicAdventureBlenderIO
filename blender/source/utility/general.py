import os
import bpy

from os.path import dirname
ADDON_DIR = dirname(dirname(dirname(os.path.realpath(__file__))))
ADDON_NAME = os.path.basename(ADDON_DIR)


def get_path():
    return ADDON_DIR


def get_name():
    return ADDON_NAME


def get_template_path():
    return f"{get_path()}\\SAIOTemplates.blend"


def compare_path(a: str, b: str):
    absolute = bpy.path.abspath(b) # pylint: disable=assignment-from-no-return
    absolute = os.path.abspath(absolute)
    return a == absolute


def load_template_blend(context: bpy.types.Context):
    lib_path = get_template_path()

    found = False
    for library in bpy.data.libraries:
        if compare_path(lib_path, library.filepath):
            found = True
            break

    if not found:
        bpy.ops.wm.link(
            filename="SAIO Material Template",
            directory=f"{lib_path}\\NodeTree\\"
        )

        bpy.ops.wm.link(
            filename="SAIO Bone Shape",
            directory=f"{lib_path}\\Object\\",
            active_collection=False,
            instance_collections=False,
            instance_object_data=False
        )

        linked_collection = None
        for col in context.scene.collection.children:
            if col.name == "Linked Data":
                linked_collection = col
                break

        if linked_collection is not None:
            try:
                link_scene = bpy.data.scenes["SAIO Links"]
            except Exception:
                link_scene = bpy.data.scenes.new("SAIO Links")
            link_scene.collection.children.link(linked_collection)
            context.scene.collection.children.unlink(linked_collection)


def is_from_template(data):
    template_path = get_template_path()
    return (
        data.library is not None
        and compare_path(template_path, data.library.filepath))


def target_anim_editor(context):
    area = [area for area in context.window.screen.areas
            if area.type == 'NLA_EDITOR'][0]

    with context.temp_override(
            area=area,
            region=area.regions[0]):

        bpy.ops.nla.tweakmode_exit(isolate_action=True)
        bpy.ops.nla.tweakmode_enter(isolate_action=True)


def get_armature_modifier(obj: bpy.types.Object) -> bpy.types.ArmatureModifier | None:

    for modifier in obj.modifiers:
        if modifier.type == 'ARMATURE':
            return modifier
    return None

def reset_property_group(target, bool_to_false: False):
    for prop in target.bl_rna.properties:
        if not hasattr(prop, "default"):
            continue

        if getattr(prop, "is_array", False):
            setattr(target, prop.identifier, prop.default_array)
        elif bool_to_false and (prop.default is True or prop.default is False):
            setattr(target, prop.identifier, False)
        else:
            setattr(target, prop.identifier, prop.default)
