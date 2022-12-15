
import bpy
from bpy.props import (
    BoolProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    EnumProperty,
    StringProperty,
    PointerProperty,
    CollectionProperty
)

from .landtable_properties import SAIO_LandTable
from .panel_properties import SAIO_PanelSettings
from .project_properties import SAIO_Project
from .quick_edit_properties import SAIO_QuickEdit
from .texture_properties import SAIO_Texture

from ...material_setup import (
    update_scene_lighting,
    update_material_outputs,
    update_materials
)


def _update_scene_lighting(self, context):
    update_scene_lighting(context)


def _update_material_outputs(self, context):
    update_material_outputs(
        bpy.data.materials,
        context.scene.saio_scene.use_principled
    )


def _update_materials(self, context):
    update_materials(context, bpy.data.materials)


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

    scene_is_level: BoolProperty(
        name="Enable Level Tools",
        description="Enables the LandTable/Level Tools for the scene.",
        default=False
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

    active_texture_index: IntProperty(
        name="Active texture index",
        description="Index of active item in texture list",
        default=-1
    )

    correct_material_textures: BoolProperty(
        name="Correct Material Texture",
        description=(
            "If a texture is being moved, the materials"
            " texture IDs will be adjusted so that"
            " materials keep their texture"
        ),
        default=True
    )

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
        subtype='COLOR_GAMMA',
        min=0,
        max=1,
        size=4,
        update=_update_scene_lighting
    )

    light_ambient_color: FloatVectorProperty(
        name="Light Ambient Color",
        description="The ambient color of the emulated light",
        default=(0.3, 0.3, 0.3, 1.0),
        subtype='COLOR_GAMMA',
        min=0,
        max=1,
        size=4,
        update=_update_scene_lighting
    )

    display_specular: BoolProperty(
        name="Viewport Specular",
        description="Display specular in the blender material view",
        default=True,
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

    # === Pointers ===

    landtable: PointerProperty(
        type=SAIO_LandTable,
        name="Quick edit properties"
    )

    texture_list: CollectionProperty(
        type=SAIO_Texture,
        name="Texture List",
        description="The textures used by sonic adventure"
    )

    project: PointerProperty(
        type=SAIO_Project,
        name="Project properties"
    )

    panels: PointerProperty(
        type=SAIO_PanelSettings,
        name="Panel properties"
    )

    viewport_panels: PointerProperty(
        type=SAIO_PanelSettings,
        name="Viewport Panel properties"
    )

    quick_edit: PointerProperty(
        type=SAIO_QuickEdit,
        name="Quick edit properties"
    )

    @classmethod
    def register(cls):
        bpy.types.Scene.saio_scene = bpy.props.PointerProperty(type=cls)
