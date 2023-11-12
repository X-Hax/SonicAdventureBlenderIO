import bpy
from bpy.props import EnumProperty, BoolProperty, IntProperty
from bpy.types import Context

from .base import SAIOBaseOperator, SAIOBasePopupOperator

from ...utility.material_setup import (
    setup_and_update_materials,
    update_material_textures,
    update_material_texids,
    get_texture_node,
    assemble_texture_list
)


class MaterialOperator(SAIOBasePopupOperator):
    bl_options = {'UNDO'}

    targetmode: EnumProperty(
        name="Target Mode",
        description="Determining which materials should be updated",
        items=(
            ("ACTIVE", "Active Material", "Only the active material"),
            ("SELECTED", "Selected objects", "Materials of selected objects"),
            ("SCENE", "Scene objects", "Materials used in the active scene"),
            ("ALL", "All", "All materials in the blend file"),
        ),
        default="SCENE"
    )

    @staticmethod
    def get_materials(context: bpy.types.Context, targetmode: str):

        results = set()

        def add(obj: bpy.types.Object):
            if obj.type == 'MESH':
                for mat in obj.data.materials:
                    results.add(mat)

        if targetmode == 'ACTIVE':
            if (context.active_object.type == 'MESH'
                    and context.active_object.active_material is not None):
                results.add(context.active_object.active_material)
        elif targetmode == 'SELECTED':
            for obj in context.selected_objects:
                add(obj)
        elif targetmode == 'SCENE':
            for obj in context.scene.objects:
                add(obj)
        else:  # ALL
            results.update(bpy.data.materials)

        return results

    def mat_execute(self, context, materials):
        pass

    @classmethod
    def poll(cls, context: Context):
        return context.mode == 'OBJECT'

    def _execute(self, context):
        materials = MaterialOperator.get_materials(context, self.targetmode)
        self.mat_execute(context, materials)
        return {'FINISHED'}


class SAIO_OT_Material_UpdateProperties(MaterialOperator):
    bl_idname = "saio.material_updateprops"
    bl_label = "Update Material Properties"
    bl_description = (
        "Setup and updates node properties to match the SAIO material"
        " properties.\n"
        " (Note: First time setup is gonna set a texture if found, but"
        " updating the material wont change the texture. Update the textures"
        " for that)"
    )

    def mat_execute(self, context, materials):
        setup_and_update_materials(context, materials)


class SAIO_OT_Material_UpdateActiveProperties(SAIOBaseOperator):
    bl_idname = "saio.material_updateactiveprops"
    bl_label = "Update Properties"
    bl_options = {'UNDO'}

    def _execute(self, context: bpy.types.Context):
        materials = MaterialOperator.get_materials(context, 'ACTIVE')
        setup_and_update_materials(context, materials)

        return {'FINISHED'}


class SAIO_OT_Material_UpdateTextures(MaterialOperator):
    bl_idname = "saio.material_updatetextures"
    bl_label = "Update Material Textures"
    bl_description = (
        "Updates either the Texture ID or the Texture Image of targeted"
        " materials. Only works on materials that have already been set up"
        " using Update Properties"
    )

    mode: EnumProperty(
        name="Mode",
        items=(
            ("IMAGE", "Texture Image",
             "Update the Image based on the texture ID"),
            ("TEXID", "Texture ID",
             "Update the texture ID based on the image set"),
        ),
        default="IMAGE"
    )

    def mat_execute(self, context, materials):
        if self.mode == 'IMAGE':
            update_material_textures(context, materials)
        else:
            update_material_texids(context, materials)


class SAIO_OT_Material_AttemptConvert(MaterialOperator):
    bl_idname = "saio.material_attemptconvert"
    bl_label = "Attempt Convert Materials"
    bl_description = (
        "Will attempt to convert non-saio materials by finding their texture"
        " and setting up an SAIO material with that texture"
    )

    assemble_texture_list: BoolProperty(
        name="Assemble Texture list",
        description=(
            "Assemble texture list from all targeted materials after"
            " converting and update their (Fallback) Texture IDs"
        ),
        default=True
    )

    global_index_offset: IntProperty(
        name="Global Index Offset",
        description="Starting global index for asembled texlist",
        default=0
    )

    def draw(self, context: Context):
        layout = self.layout

        layout.prop(self, "targetmode")
        layout.prop(self, "assemble_texture_list")

        if self.assemble_texture_list:
            layout.prop(self, "global_index_offset")

    def mat_execute(
            self,
            context: bpy.types.Context,
            materials: set[bpy.types.Material]):

        to_convert = dict()
        for material in materials:
            tex_node = get_texture_node(material)
            if tex_node is None and material.node_tree is not None:
                image = None
                for node in material.node_tree.nodes:
                    if isinstance(node, bpy.types.ShaderNodeTexImage):
                        image = node.image
                        break

                to_convert[material] = image

        setup_and_update_materials(context, to_convert.keys())

        for material, texture in to_convert.items():
            if texture is not None:
                tex_node = get_texture_node(material)
                tex_node.image = texture
                material.saio_material.use_texture = True

        if self.assemble_texture_list:
            world = assemble_texture_list(
                materials, self.global_index_offset)
            context.scene.saio_scene.texture_world = world
            update_material_texids(context, materials)


class SAIO_OT_Material_AssembleTextureList(SAIOBasePopupOperator):
    bl_idname = "saio.material_assembletexlist"
    bl_label = "Assemble Texture List"
    bl_description = (
        "Collects textures used in the scene/event and creates a new world"
        " with a texture list containing them, ready for export. Also"
        " updates sourced materials."
    )
    bl_options = {'UNDO'}

    mode: EnumProperty(
        name="Mode",
        items=(
            ("SCENE", "Scene", ""),
            ("EVE", "Event", ""),
        ),
        default="SCENE",
    )

    global_index_offset: IntProperty(
        name="Global Index Offset",
        description="Starting global index",
        default=0
    )

    def _execute(self, context: bpy.types.Context):

        base_scene = None
        scenes = set()
        if self.mode == 'SCENE':
            scenes.add(context.scene)
        else:
            from ...exporting.o_event import get_base_scene
            base_scene = get_base_scene(context)

            scenes = set()
            scenes.add(base_scene)
            for scene in base_scene.saio_scene.event:
                if scene.scene is not None:
                    scenes.add(scene.scene)

        objects = set()
        for scene in scenes:
            objects.update(scene.objects)

        materials = set()
        for obj in objects:
            if obj.type == 'MESH':
                materials.update(obj.data.materials)

        world = assemble_texture_list(
            materials, self.global_index_offset)

        for scene in scenes:
            scene.saio_scene.texture_world = world

        update_material_texids(context, materials)

        return {'FINISHED'}
