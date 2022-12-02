
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

from . import (
    landtable,
    panel_properties,
    quick_edit,
    project,
    texture
)


class SAIO_Settings(bpy.types.PropertyGroup):
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
        size=3
    )

    light_color: FloatVectorProperty(
        name="Light Color",
        description="The color of the emulated light",
        default=(1.0, 1.0, 1.0),
        subtype='COLOR_GAMMA',
        min=0,
        max=1,
        size=3
    )

    light_ambient_color: FloatVectorProperty(
        name="Light Ambient Color",
        description="The ambient color of the emulated light",
        default=(0.3, 0.3, 0.3),
        subtype='COLOR_GAMMA',
        min=0,
        max=1,
        size=3
    )

    display_specular: BoolProperty(
        name="Viewport Specular",
        description="Display specular in the blender material view",
        default=True
    )

    viewport_alpha_type: EnumProperty(
        name="Viewport Alpha Type",
        description="The Eevee alpha type to display transparent materials",
        items=(('BLEND', "Blend", "The default blending"),
               ('HASHED', "Hashed", "Hashed transparency"),
               ('CLIP', "Clip", "Sharp edges for certain thresholds")),
        default='BLEND'
    )

    viewport_alpha_cutoff: FloatProperty(
        name="Viewport blend Cutoff",
        description="Cutoff value for the eevee alpha cutoff transparency",
        min=0,
        max=1,
        default=0.5
    )

    # === Pointers ===

    landtable: PointerProperty(
        type=landtable.SAIO_LandTable,
        name="Quick edit properties"
    )

    texture_list: CollectionProperty(
        type=texture.SAIO_Texture,
        name="Texture List",
        description="The textures used by sonic adventure"
    )

    project: PointerProperty(
        type=project.SAIO_Project,
        name="Project properties"
    )

    panels: PointerProperty(
        type=panel_properties.SAIO_PanelSettings,
        name="Panel properties"
    )

    viewport_panels: PointerProperty(
        type=panel_properties.SAIO_PanelSettings,
        name="Viewport Panel properties"
    )

    quick_edit: PointerProperty(
        type=quick_edit.SAIO_QuickEdit,
        name="Quick edit properties"
    )

    @classmethod
    def register(cls):
        bpy.types.Scene.saio_settings = bpy.props.PointerProperty(type=cls)
