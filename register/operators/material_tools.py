import bpy
from bpy.types import Operator

from bpy.props import (
    EnumProperty,
    BoolProperty
)

from ...material_setup import update_materials


def _get_materials(context: bpy.types.Context, mode: str):

    results = []

    def add(object: bpy.types.Object):
        if object.type == 'MESH' and object.active_material is not None:
            results.append(object.active_material)

    if mode == 'ACTIVE':
        add(context.active_object)
    elif mode == 'SELECTED':
        for obj in context.selected_objects:
            add(obj)
    elif mode == 'SCENE':
        for obj in context.scene.objects:
            add(obj)
    else:  # ALL
        results = [mat for mat in bpy.data.materials]

    return results


class SAIO_OT_Material_TextureFromID(Operator):
    bl_idname = "saio.material_texturefromid"
    bl_label = "Texture from ID"
    bl_description = (
        "Sets the textures of materials to"
        " corresponding (fallback) texture ids"
    )


class SAIO_OT_Material_TextureToID(Operator):
    bl_idname = "saio.material_texturetoid"
    bl_label = "Texture to ID"
    bl_description = (
        "Sets the (fallback) texture ids of materials"
        " to that of the selected texture"
    )


class SAIO_OT_Material_UpdateNodes(Operator):
    bl_idname = "saio.material_updatenodes"
    bl_label = "Update material nodes"

    mode: EnumProperty(
        name="Mode",
        description="Determining which materials should be updated",
        items=(
            ("ACTIVE", "Active Material", "Only the active material"),
            ("SELECTED", "Selected objects", "Materials of selected objects"),
            ("SCENE", "Scene objects", "Materials used in the active scene"),
            ("ALL", "All", "All materials in the blend file"),
        ),
        default="SELECTED"
    )

    use_principled: BoolProperty(
        name="Use Principled BSDF",
        description="Hook up a principled node instead of "
    )

    def execute(self, context: bpy.types.Context):

        materials = _get_materials(context, self.mode)
        update_materials(context, materials)

        return {'FINISHED'}
