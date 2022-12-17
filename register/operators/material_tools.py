import bpy
from bpy.types import Operator

from bpy.props import (
    EnumProperty,
    BoolProperty
)

from ...material_setup import update_materials

material_selection = (
    ("ACTIVE", "Active Material", "Only the active material"),
    ("SELECTED", "Selected objects", "Materials of selected objects"),
    ("SCENE", "Scene objects", "Materials used in the active scene"),
    ("ALL", "All", "All materials in the blend file"),
),


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
    bl_options = {'REGISTER', 'UNDO'}

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

    def execute(self, context: bpy.types.Context):
        materials = _get_materials(context, self.properties.mode)
        texture_list = context.scene.saio_scene.texture_list

        for material in materials:
            try:
                texture_node: bpy.types.ShaderNodeTexImage \
                    = material.node_tree.nodes["SAIO Texture"]

                index = material.saio_material.texture_id
                if index >= len(texture_list.textures):
                    continue

                texture_node.image = texture_list.textures[index].image

            except Exception:
                continue

        return {'FINISHED'}


class SAIO_OT_Material_TextureToID(Operator):
    bl_idname = "saio.material_texturetoid"
    bl_label = "Texture to ID"
    bl_description = (
        "Sets the (fallback) texture ids of materials"
        " to that of the selected texture"
    )
    bl_options = {'REGISTER', 'UNDO'}

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

    add_missing_textures: BoolProperty(
        name="Add missing texture to list",
        description=(
            "If a material uses a texture that is not used in the"
            " texture list, it will be added"
        ),
        default=True
    )

    def execute(self, context: bpy.types.Context):
        materials = _get_materials(context, self.mode)
        texture_list = context.scene.saio_scene.texture_list

        for material in materials:
            try:
                texture_node: bpy.types.ShaderNodeTexImage \
                    = material.node_tree.nodes["SAIO Texture"]

                index = texture_list.get_index(texture_node.image)
                if index is None:
                    if self.add_missing_textures:
                        texture_list.new(image=texture_node.image)
                        index = len(texture_list.textures) - 1
                    else:
                        continue

                material.saio_material.texture_id = index

            except Exception:
                continue

        return {'FINISHED'}


class SAIO_OT_Material_UpdateNodes(Operator):
    bl_idname = "saio.material_updatenodes"
    bl_label = "Update material nodes"
    bl_options = {'REGISTER', 'UNDO'}

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

    def execute(self, context: bpy.types.Context):
        materials = _get_materials(context, self.properties.mode)
        update_materials(context, materials)

        return {'FINISHED'}


class SAIO_OT_Material_UpdateActiveNodes(Operator):
    bl_idname = "saio.material_updateactivenodes"
    bl_label = "Update nodes"

    def execute(self, context: bpy.types.Context):
        materials = _get_materials(context, 'ACTIVE')
        update_materials(context, materials)

        return {'FINISHED'}
