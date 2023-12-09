
import bpy
from bpy.props import (
    BoolProperty,
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
    StringProperty,
    PointerProperty,
)

from .event_properties import SAIO_Event
from .landtable_properties import SAIO_LandTable
from .panel_properties import SAIO_PanelSettings
from .material_mass_edit_properties import SAIO_MaterialMassEdit
from .texture_properties import SAIO_TextureList
from .texturename_properties import SAIO_TextureNameList

from ...utility.material_setup import (
    update_scene_lighting,
    update_material_outputs,
    update_material_values
)


def _update_scene_lighting(self, context): # pylint: disable=unused_argument
    update_scene_lighting(context)


def _update_material_outputs(self, context): # pylint: disable=unused_argument
    update_material_outputs(
        bpy.data.materials,
        context.scene.saio_scene.use_principled
    )


def _update_materials(self, context):
    sceneprops = context.scene.saio_scene
    blend_method = sceneprops.viewport_alpha_type
    clip_threshold = sceneprops.viewport_alpha_cutoff
    enable_backface_culling = sceneprops.enable_backface_culling

    for material in bpy.data.materials:
        update_material_values(
            material, blend_method, clip_threshold, enable_backface_culling)


class SAIO_Scene(bpy.types.PropertyGroup):
    """Property Groups used across the Addon"""

    author: StringProperty(
        name="Author",
        description="The creator of this file",
        default="",
    )

    description: StringProperty(
        name="Description",
        description="A Description of the file contents",
        default="",
    )

    scene_type: EnumProperty(
        name="Scene type",
        description="Enables specific SAIO tools for the scene.",
        items=[
            ("MDL", "Model", "Model file"),
            ("LVL", "Landtable", "Landtable file"),
            ("EVR", "SA2 Event Root", "SA2 Event root/base scene"),
            ("EVC", "SA2 Event Scene", "SA2 Event cut/sub scene"),
        ],
        default="MDL"
    )

    use_principled: BoolProperty(
        name="Use Principled BSDF",
        description=(
            "When checked, blender hooks up the principled"
            " node to the material output so that the models"
            " can be exported with material information"
        ),
        default=False,
        update=_update_material_outputs
    )

    checked_for_migrate_data: BoolProperty()
    found_migrate_data: BoolProperty(default=True)

    # === Lighting ===

    light_dir: FloatVectorProperty(
        name="Light Direction",
        description=(
            "The direction of the emulated light"
            " (seen from the y+ axis)"
        ),
        subtype='DIRECTION',
        default=(0.0, 0.0, 1.0),
        min=0,
        max=1,
        size=3,
        update=_update_scene_lighting
    )

    light_color: FloatVectorProperty(
        name="Light Color",
        description="The color of the emulated light",
        default=(1.0, 1.0, 1.0, 1.0),
        subtype='COLOR',
        min=0,
        max=1,
        size=4,
        update=_update_scene_lighting
    )

    light_ambient_color: FloatVectorProperty(
        name="Light Ambient Color",
        description="The ambient color of the emulated light",
        default=(0.3, 0.3, 0.3, 1.0),
        subtype='COLOR',
        min=0,
        max=1,
        size=4,
        update=_update_scene_lighting
    )

    display_specular: BoolProperty(
        name="Viewport Specular",
        description="Display specular in the blender material view",
        default=False,
        update=_update_scene_lighting
    )

    viewport_alpha_type: EnumProperty(
        name="Viewport Alpha Type",
        description="The Eevee alpha type to display transparent materials",
        items=(('BLEND', "Blend", "The default blending"),
               ('HASHED', "Hashed", "Hashed transparency"),
               ('CLIP', "Clip", "Sharp edges for certain thresholds")),
        default='BLEND',
        update=_update_materials
    )

    viewport_alpha_cutoff: FloatProperty(
        name="Viewport blend Cutoff",
        description="Cutoff value for the eevee alpha cutoff transparency",
        min=0, max=1,
        default=0.5,
        update=_update_materials
    )

    enable_backface_culling: BoolProperty(
        name="Enabl Backface Culling",
        description=(
            "Enables backface culling"
            " (for materials that disabled double sided)"
        ),
        default=False,
        update=_update_materials
    )

    # === Pointers ===

    landtable: PointerProperty(
        type=SAIO_LandTable,
        name="Landtable"
    )

    event: PointerProperty(
        type=SAIO_Event,
        name="SA2 Event"
    )

    texture_world: PointerProperty(
        type=bpy.types.World,
        name="Texture list storage"
    )

    texturename_world: PointerProperty(
        type=bpy.types.World,
        name="Texturename list storage",
    )

    panels: PointerProperty(
        type=SAIO_PanelSettings,
        name="Panel properties"
    )

    viewport_panels: PointerProperty(
        type=SAIO_PanelSettings,
        name="Viewport Panel properties"
    )

    material_mass_edit: PointerProperty(
        type=SAIO_MaterialMassEdit,
        name="Material mass edit parameters"
    )

    @classmethod
    def register(cls):
        bpy.types.Scene.saio_scene = bpy.props.PointerProperty(type=cls) # pylint: disable=assignment-from-no-return

    @property
    def texture_list(self) -> SAIO_TextureList | None:
        if self.texture_world is None:
            return None
        return self.texture_world.saio_texture_list

    @property
    def texturename_list(self) -> SAIO_TextureNameList | None:
        if self.texturename_world is None:
            return None
        return self.texturename_world.saio_texturename_list

    @staticmethod
    def check_is_landtable(context: bpy.types.Context | None = None):
        if context is None:
            context = bpy.context

        if not context.scene.saio_scene.scene_type == 'LVL':
            return "Scene is not marked as Landtable"

        return None

    @staticmethod
    def check_is_event(context: bpy.types.Context = None):
        if context is None:
            context = bpy.context

        if context.scene.saio_scene.scene_type not in {'EVR', 'EVC'}:
            return "Scene not marked as Event"

        return None

    @staticmethod
    def check_is_event_root(context: bpy.types.Context = None):
        if context is None:
            context = bpy.context

        if not context.scene.saio_scene.scene_type == 'EVR':
            return "Scene not marked as Event root"

        return None
