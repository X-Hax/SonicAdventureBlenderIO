import bpy
from .base import SAIOBaseOperator


class SAIO_OT_Info_Manual(SAIOBaseOperator):
    bl_idname = "saio.info_manual"
    bl_label = "Open Manual"
    bl_description = "Opens the online manual for the addon"

    def _execute(self, context: bpy.types.Context):
        import webbrowser
        webbrowser.open("https://x-hax.github.io/SonicAdventureBlenderIO/")
        return {'FINISHED'}


class SAIO_OT_Info_Discord(SAIOBaseOperator):
    bl_idname = "saio.info_discord"
    bl_label = "Open Discord Server"
    bl_description = "Opens the discord server invite link"

    def _execute(self, context: bpy.types.Context):
        import webbrowser
        webbrowser.open("https://discord.gg/gqJCF47")
        return {'FINISHED'}
