import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty
)


class SAIO_PanelSettings(bpy.types.PropertyGroup):
    """Property Group for managing expanded menus"""

    # === Material ===

    expanded_texture_properties: BoolProperty(
        name="Texture properties",
        default=False
    )

    expanded_rendering_properties: BoolProperty(
        name="Rendering properties",
        default=False
    )

    expanded_gc_properties: BoolProperty(
        name="SA2B specific",
        default=False
    )

    expanded_gc_texgen: BoolProperty(
        name="Generate texture coords",
        default=False
    )

    # === Land Entry ===

    expanded_surface_attributes: BoolProperty(
        name="Surface Attributes",
        default=False
    )

    advanced_surface_attributes: BoolProperty(
        name="Advanced Surface Attributes",
        description=(
            "Show unknown attributes."
            "\nWARNING: Unknown surface flags are likely to get renamed in the"
            " future as research pushes forward, losing their value when such"
            " an update happens!"
        ),
        default=False
    )

    land_entry_surface_attributes_editmode: EnumProperty(
        name="Surface attributes edit mode",
        description="How to edit the surface flags",
        items=(
             ("UNIVERSAL", "Universal",
                 "edit all surface attributes simultaneously"),
            ("SA1", "Adventure 1",
                 "Edit surface attributes specific to sa1"),
            ("SA2", "Adventure 2",
                 "Edit surface attributes specific to sa2"),
        ),
        default="UNIVERSAL"
    )

    # == Event ==

    expanded_override_upgrade_menu: BoolProperty(
        name="Integrated Upgrades",
        default=False
    )

    override_upgrade_menu: EnumProperty(
        name="Upgrade",
        items=[
            ("SONLS", "Sonic Light Shoes", ""),
            ("SONAL", "Sonic Ancient Light", ""),
            ("SONMG", "Sonic Magic Gloves", ""),
            ("SONFR", "Sonic Flame Ring", ""),
            ("SONBB", "Sonic Bounce Bracelet", ""),
            ("SONMM", "Sonic Mystic Melody", ""),

            ("TAIBS", "Tails Booster", ""),
            ("TAIBZ", "Tails Bazooka", ""),
            ("TAILB", "Tails Laser Blaster", ""),
            ("TAIMM", "Tails Mystic Melody", ""),

            ("KNUSC", "Knuckles Shovel Claws", ""),
            ("KNUSG", "Knuckles Sunglasses", ""),
            ("KNUHG", "Knuckles Hammer Gloves", ""),
            ("KNUAN", "Knuckles Air Necklace", ""),
            ("KNUMM", "Knuckles Mystic Melody", ""),

            ("SONSU", "Super Sonic", ""),

            ("SHAAS", "Shadow Air Shoes", ""),
            ("SHAAL", "Shadow Ancient Light", ""),
            ("SHAFR", "Shadow Flame Ring", ""),
            ("SHAMM", "Shadow Mystic Melody", ""),
            ("EGGJE", "Eggman Jet Engine", ""),

            ("EGGLC", "Eggman Large Cannon", ""),
            ("EGGLB", "Eggman Laser Blaster", ""),
            ("EGGPA", "Eggman Protective Armor", ""),
            ("EGGMM", "Eggman Mystic Melody", ""),
            ("ROUPN", "Rouge Pick Nails", ""),

            ("ROUTS", "Rouge Treasure Scope", ""),
            ("ROUIB", "Rouge Iron Boots", ""),
            ("ROUMM", "Rouge MysticMelody", ""),
        ],
        default="SONLS"
    )

    expanded_attach_upgrade_menu: BoolProperty(
        name="Overlay Upgrades",
        default=False
    )

    attach_upgrade_menu: EnumProperty(
        name="Upgrade",
        items=[
            ("SONLS", "Sonic Light Shoes", ""),
            ("SONFR", "Sonic Flame Ring", ""),
            ("SONBB", "Sonic Bounce Bracelet", ""),
            ("SONMG", "Sonic Magic Gloves", ""),

            ("SHAAS", "Shadow Air Shoes", ""),
            ("SHAFR", "Shadow Flame Ring", ""),

            ("KNUS1", "Knuckles Shovel Claws 1", ""),
            ("KNUS2", "Knuckles Shovel Claws 2", ""),
            ("KNUH1", "Knuckles Hammer Gloves 1", ""),
            ("KNUH2", "Knuckles Hammer Gloves 2", ""),
            ("KNUSG", "Knuckles Sunglasses", ""),
            ("KNUAN", "Knuckles Air Necklace", ""),

            ("ROUPN", "Rouge Pick Nails", ""),
            ("ROUTS", "Rouge Treasure Scope", ""),
            ("ROUIB", "Rouge Iron Boots", ""),

            ("ROUSP", "Rouge Shoe Plates (Transparency)", ""),
            ("TAIWS", "Tails Windshield (Transparency)", ""),
            ("EGGWS", "Eggman Windshield (Transparency)", ""),
        ],
        default="SONLS"
    )

    expanded_uv_animations_menu: BoolProperty(
        name="UV Animations",
        default=False
    )

    # === Scene ===

    expanded_lighting_panel: BoolProperty(
        name="Lighting Data",
        default=False
    )
