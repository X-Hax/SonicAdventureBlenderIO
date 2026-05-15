import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    PointerProperty,
    IntProperty
)


class SAIO_EventEntry(bpy.types.PropertyGroup):
    """SA2 Event entry Settings"""

    entry_type: EnumProperty(
        name="Entry Type",
        items=[
            ("NONE", "None", "Not event related"),
            ("CHUNK", "Chunk", "Default model type"),
            ("GC", "GC", "Gamecube type, only valid for sa2b cutscenes"),
            ("SHADOW", "GC Shadow", "Shadow model for sa2b cutscenes"),
            ("PARTICLE", "Particle", "Container for particle animations"),
            ("REFLECTION", "Reflection Plane", "Reflection plane"),
        ],
        default="CHUNK"
    )

    shadow_model: PointerProperty(
        name="GC Shadow model",
        type=bpy.types.Object
    )

    has_environment: BoolProperty(
        name="Has Environment",
        description="Has environment mapped materials, use Simple variant of draw function.",
        default=False
    )

    no_fog_and_easy_draw: BoolProperty(
        name="No Fog & Easy Draw",
        description="Draw with fog disabled and use EasyDraw",
        default=False
    )

    light1: BoolProperty(
        name="Light 1",
        description="Use multi-light 1",
        default=False
    )

    light2: BoolProperty(
        name="Light 2",
        description="Use multi-light 2",
        default=False
    )

    light3: BoolProperty(
        name="Light 3",
        description="Use multi-light 3",
        default=False
    )

    light4: BoolProperty(
        name="Light 4",
        description="Use multi-light 4",
        default=False
    )

    modifier_volume: BoolProperty(
        name="Modifier Volume",
        description="Is a modifier volume and should use ModDraw.",
        default=False
    )

    reflection: BoolProperty(
        name="Reflection",
        description="Object gets rendered as part of reflections",
        default=False
    )

    blare: BoolProperty(
        name="Blare",
        description=(
            "Perform blare on this model"
            " (unused, by default broken effect)"
        ),
        default=False
    )

    use_simple: BoolProperty(
        name="Use Simple",
        description="Use regular Simple over any Multi or Easy variant",
        default=False
    )

    layer: IntProperty(
        name="Layer",
        description=(
            "Battle: Render Layer; Determines render order for transparent"
            " models"
        ),
        default=0
    )

    @classmethod
    def register(cls):
        bpy.types.Object.saio_event_entry = PointerProperty(type=cls) # pylint: disable=assignment-from-no-return

    @staticmethod
    def check_is_event_entry(obj: bpy.types.Object):

        if obj.type not in ['MESH', 'EMPTY', 'ARMATURE']:
            return "Object not a valid type to be entry"

        if obj.parent is not None:
            return "Object not hierarchy root"

        return None
