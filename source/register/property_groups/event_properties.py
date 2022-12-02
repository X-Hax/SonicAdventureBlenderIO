import bpy
from bpy.props import (
    StringProperty,
    PointerProperty,
    CollectionProperty,
    BoolProperty
)
from .base_list import BaseList
from .event_uv_anim_properties import SAIO_Event_UVAnimList


class SAIO_EventScene(bpy.types.PropertyGroup):

    name: StringProperty(
        name="Name",
        default="Scene"
    )

    scene: PointerProperty(
        type=bpy.types.Scene,
        name="Scene"
    )


class SAIO_OverrideUpgrade(bpy.types.PropertyGroup):

    base: PointerProperty(
        type=bpy.types.Object,
        name="Base"
    )

    base_bone: StringProperty(
        name="Base Bone"
    )

    override1: PointerProperty(
        type=bpy.types.Object,
        name="Override 1"
    )

    override1_bone: StringProperty(
        name="Override 1 Bone"
    )

    override2: PointerProperty(
        type=bpy.types.Object,
        name="Override 2"
    )

    override2_bone: StringProperty(
        name="Override 2 Bone"
    )


class SAIO_AttachUpgrade(bpy.types.PropertyGroup):

    model1: PointerProperty(
        type=bpy.types.Object,
        name="Model 1"
    )

    target1: PointerProperty(
        type=bpy.types.Object,
        name="Target 1"
    )

    target1_bone: StringProperty(
        name="Target 1 Bone"
    )

    model2: PointerProperty(
        type=bpy.types.Object,
        name="Model 2"
    )

    target2: PointerProperty(
        type=bpy.types.Object,
        name="Target 2"
    )

    target2_bone: StringProperty(
        name="Target 2 Bone"
    )


class SAIO_Event(BaseList):
    """SA2 Root event properties"""

    elements: CollectionProperty(
        type=SAIO_EventScene,
        name="Scenes list",
        description="Scenes, in order, of export. Supports reuse of scenes"
    )

    drop_shadow_control: BoolProperty(
        name="Drop Shadow Control",
        default=False
    )

    tails_tails: PointerProperty(
        type=bpy.types.Object,
        name="Tails Tails"
    )

    tails_tails_bone: StringProperty(
        name="Tails Tails Bone"
    )

    uv_animations: PointerProperty(
        name="UV Animations",
        type=SAIO_Event_UVAnimList
    )

    ou_sonls: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_sonal: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_sonmg: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_sonfr: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_sonbb: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_sonmm: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_taibs: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_taibz: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_tailb: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_taimm: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_knusc: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_knusg: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_knuhg: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_knuan: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_knumm: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_sonsu: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_shaas: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_shaal: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_shafr: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_shamm: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_eggje: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_egglc: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_egglb: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_eggpa: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_eggmm: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_roupn: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_routs: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_rouib: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_roumm: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_add01: PointerProperty(type=SAIO_OverrideUpgrade)
    ou_add02: PointerProperty(type=SAIO_OverrideUpgrade)

    au_sonls: PointerProperty(type=SAIO_AttachUpgrade)
    au_sonfr: PointerProperty(type=SAIO_AttachUpgrade)
    au_sonbb: PointerProperty(type=SAIO_AttachUpgrade)
    au_sonmg: PointerProperty(type=SAIO_AttachUpgrade)
    au_shaas: PointerProperty(type=SAIO_AttachUpgrade)
    au_shafr: PointerProperty(type=SAIO_AttachUpgrade)
    au_knus1: PointerProperty(type=SAIO_AttachUpgrade)
    au_knus2: PointerProperty(type=SAIO_AttachUpgrade)
    au_knuh1: PointerProperty(type=SAIO_AttachUpgrade)
    au_knuh2: PointerProperty(type=SAIO_AttachUpgrade)
    au_knusg: PointerProperty(type=SAIO_AttachUpgrade)
    au_knuan: PointerProperty(type=SAIO_AttachUpgrade)
    au_roupn: PointerProperty(type=SAIO_AttachUpgrade)
    au_routs: PointerProperty(type=SAIO_AttachUpgrade)
    au_rouib: PointerProperty(type=SAIO_AttachUpgrade)
    au_rousp: PointerProperty(type=SAIO_AttachUpgrade)
    au_taiws: PointerProperty(type=SAIO_AttachUpgrade)
    au_eggws: PointerProperty(type=SAIO_AttachUpgrade)

    @classmethod
    def _get_index_comparator(cls, value):
        if isinstance(value, str):
            return lambda x: x.name == value
        elif isinstance(value, SAIO_EventScene):
            return lambda x: x == value
        elif isinstance(value, bpy.types.Scene):
            return lambda x: x.scene == value
        raise NotImplementedError()

    def _on_created(self, value, **args):
        if "scene" in args:
            value.scene = args["scene"]

        if "name" in args:
            value.name = args["name"]
        elif value.scene is not None:
            value.name = value.scene.name
        else:
            value.name = "Scene"
