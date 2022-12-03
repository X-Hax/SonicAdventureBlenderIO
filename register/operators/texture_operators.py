import os
import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy.props import (
    EnumProperty,
    StringProperty,
)

from ...text.sa_texture import SATextureFile
from ..property_groups import (
    SAIO_Scene,
    SAIO_Material
)


class SAIO_OT_Textures_Add(Operator):
    """Adds a texture slot to the Scene Texture List."""
    bl_idname = "saio.textures_add"
    bl_label = "Add texture"
    bl_description = "Adds texture to the texture list"

    def execute(self, context):
        settings: SAIO_Scene = context.scene.saio_scene

        # getting next usable global id
        ids = [t.global_id for t in settings.texture_list]
        ids.sort(key=lambda x: x)

        global_id = len(settings.texture_list)
        for i, index in enumerate(ids):
            if i != index:
                global_id = i
                break

        # creating texture
        tex = settings.texture_list.add()
        settings.active_texture_index = len(settings.texture_list) - 1

        tex.name = "Texture"
        tex.global_id = global_id

        return {'FINISHED'}


class SAIO_OT_Textures_Remove(Operator):
    """Removes the selected texture slot from the Scene Texture List."""
    bl_idname = "saio.textures_remove"
    bl_label = "Remove texture"
    bl_description = "Removes the selected texture from the texture list"

    def execute(self, context):
        settings: SAIO_Scene = context.scene.saio_scene
        settings.texture_list.remove(settings.active_texture_index)

        settings.active_texture_index -= 1
        if len(settings.texture_list) == 0:
            settings.active_texture_index = -1
        elif settings.active_texture_index < 0:
            settings.active_texture_index = 0

        return {'FINISHED'}


class SAIO_OT_Textures_Move(Operator):
    """Moves the selected texture slot in the Scene Texture List."""
    bl_idname = "saio.textures_move"
    bl_label = "Move texture"
    bl_description = "Moves texture slot in list"

    direction: EnumProperty(
        name="Direction",
        items=(
            ('UP', "up", "up"),
            ('DOWN', "down", "down"),
        )
    )

    def execute(self, context):
        settings: SAIO_Scene = context.scene.saio_scene

        new_index = (
            settings.active_texture_index
            + (-1 if self.direction == 'UP'
               else 1)
        )

        if new_index != -1 and new_index < len(settings.texture_list):

            if settings.correct_material_textures:
                for m in bpy.data.materials:
                    props: SAIO_Material = m.saio_material
                    if props.texture_id == new_index:
                        props.texture_id = settings.active_texture_index
                    elif props.texture_id == settings.active_texture_index:
                        props.texture_id = new_index

            settings.texture_list.move(
                settings.active_texture_index,
                new_index)

            settings.active_texture_index = new_index
        return {'FINISHED'}


class SAIO_OT_Textures_Autoname(Operator):
    """Autonames Texture List entries based on their assigned image names."""
    bl_idname = "saio.textures_autoname"
    bl_label = "Autoname entries"
    bl_description = "Renames all entries to the assigned texture"

    def execute(self, context):
        tex_list = context.scene.saio_scene.texture_list

        for t in tex_list:
            if t.image is not None:
                t.name = os.path.splitext(t.image.name)[0]
            else:
                t.name = "Texture"
        return {'FINISHED'}


class SAIO_OT_Textures_Clear(Operator):
    """Clears all entries from the Scene Texture List."""
    bl_idname = "saio.textures_clear"
    bl_label = "Clear list"
    bl_description = "Removes all entries from the list"

    def execute(self, context):
        settings = context.scene.saio_scene
        settings.active_texture_index = -1

        for t in settings.texture_list:
            if t.image is not None:
                t.image.use_fake_user = False

        settings.texture_list.clear()
        return {'FINISHED'}


class SAIO_OT_Textures_Import(Operator, ImportHelper):
    """Imports texture archives. Only texture packs supported currently."""
    bl_idname = "saio.textures_import"
    bl_label = "Import SA tex file"

    filter_glob: StringProperty(
        default="*.pak;*.gvm;*.pvm;*.pvmx;*.txt;*.tls;*.satex",
        options={'HIDDEN'},
    )

    def invoke(self, context, event):
        wm = context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def stop(self):
        self.report({'WARNING'}, "File not a valid texture file!")
        return {'CANCELLED'}

    def load_texture_list(
            self,
            context: bpy.types.Context,
            textures: list[tuple[int, str]]):
        bpy.ops.saio.textures_clear()
        texture_list = context.scene.saio_scene.texture_list

        for i, t in textures:
            img = None

            for image in bpy.data.images:
                if image.filepath == t:
                    img = image
                    break

            if img is None:
                img = bpy.data.images.load(t)

            img.use_fake_user = True
            tex = texture_list.add()
            tex.global_id = i
            tex.name = os.path.splitext(os.path.basename(t))[0]
            tex.image = img

    def _read_txt(self, folder: str) -> list[tuple[int, str]]:

        content: list[str] = None
        with open(self.filepath) as f:
            content = f.readlines()

        # validating index file
        result = []
        for c in content:
            c = c.strip().split(',')
            if len(c) < 2:
                return self.stop()

            try:
                gIndex = int(c[0])
            except Exception:
                return self.stop()

            texturePath = folder + "\\" + c[1]
            if not os.path.isfile(texturePath):
                return self.stop()

            result.append((gIndex, texturePath))

        return result

    def _read_tls(self, folder: str) -> list[tuple[int, str]]:

        content: list[str] = None
        with open(self.filepath) as f:
            content = f.readlines()

        result = []
        for c in content:
            c = c.strip().split('.')
            texturePath = folder + "\\" + c[0] + ".png"

            if not (os.path.isfile(texturePath)):
                return self.stop()

            result.append((0, texturePath))

        return result

    def _read_satex(self, folder: str) -> list[tuple[int, str]]:
        satexf = SATextureFile()
        satexf.fromIni(self.filepath)

        result = []
        for c in satexf.texture_names:
            texturePath = folder + "\\" + c
            if not (os.path.isfile(texturePath)):
                return self.stop()
            result.append((0, texturePath))

        return result

    def execute(self, context):
        import os
        extension = os.path.splitext(self.filepath)[1]
        folder = os.path.dirname(self.filepath)

        if extension == '.txt':
            textures = self._read_txt(folder)
        elif extension == '.tls':
            textures = self._read_tls(folder)
        elif extension == '.satex':
            textures = self._read_satex(folder)
        else:
            return {'FINISHED'}

        self.load_texture_list(context, textures)
        return {'FINISHED'}
