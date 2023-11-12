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

    layer: IntProperty(
        name="Layer",
        description=(
            "Battle: Render Layer; Determines render order for transparent"
            " models"
        ),
        default=0
    )

    unk0: BoolProperty(
        name="unknown 0",
        default=False
    )

    unk2: BoolProperty(
        name="unknown 2",
        default=False
    )

    unk4: BoolProperty(
        name="unknown 4",
        default=False
    )

    unk5: BoolProperty(
        name="unknown 5",
        default=False
    )

    unk6: BoolProperty(
        name="unknown 6",
        default=False
    )

    unk9: BoolProperty(
        name="unknown 9",
        default=False
    )

    enable_lighting: BoolProperty(
        name="Enable Lighting",
        description="Enables lighting (root scene only)",
        default=True
    )

    disable_shadow_catching: BoolProperty(
        name="Disable shadow catching",
        description=(
            "Prevents shadows from being drawn on this model"
            " (root scene, GC models only)"
        ),
        default=False
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
