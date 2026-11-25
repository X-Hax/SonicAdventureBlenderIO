import bpy
from bpy.props import (
    PointerProperty,
    IntProperty,
    EnumProperty,
    BoolProperty,
    StringProperty
)

from .mesh_properties import MESH_DATA_TYPES

def _get_blockbit_hex(data: any):
    return f"{data.blockbit:08X}"

def _set_blockbit_hex(data: any, value: str):
    try:
        data.blockbit = int(value, 16)
    except:
        pass

def _set_flag(
    data: any,
    property: str,
    shift: int,
    value: bool):

    current = getattr(data, property)

    if shift == 31:
        mask = -2147483648
    else:
        mask = 1 << shift
    
    if value:
        new = current | mask
    else:
        new = current & ~mask

    setattr(data, property, new)

SA1_SURFACE_ATTRIBUTES = [
    ("Solid", "Solid collision", None, "COL"),
    ("Water", "Water flag (ripples, breath counter, heavy physics)", None, "COL"),
    ("Ice", "Ice behavior, friction is 0.1", [0], "COL"),
    ("Snow", "Snowboard terrain, friction is 0.15", [0], "COL"),
    ("Sand", "Sandboard terrain, friction is 0.5", [0], "COL"),
    ("Use Sky Draw-distance", "Uses the skybox draw distance instead of the level draw distance", [31], "VIS"),
    ("Cannot Land", "Surface will prevent players from standing on it", [0], "COL"),
    ("High Friction", "Terrain friction is 1.5", [0], "COL"),
    ("Diggable", "Knuckles can dig", [0], "COL"),
    ("No Camera Collision", "Unused, but likely intended to be used for disabling collision with the camera", [0], "COL"),
    ("Waterfall", "Mystic Ruin waterfalls (Force alpha sorting; Disable Z Write when used together with Water; Force disable Z write in all levels except Lost World 2)", [31], "VIS"),
    ("Waterslide", "Unused, but found on lost world waterslide ", [0], "COL"),
    ("Unclimbable", "Surface cannot be climbed by Knuckles", [0], "COL"),
    ("Chaos 0 Land", "Turns off Visible when Chaos 0 jumps up a pole", [31], "VIS"),
    ("Stairs", "Stairs behavior (upward normal, high floor grip)", [0], "COL"),
    ("Lava", "Unused, but likely intended to be used for lava surfaces", [0], "COL"),
    ("Contact damage", "Collision inflicts damage on the player", [0], "COL"),
    ("Tube", "Improves character rotation against floor and camera angles. Also has dedicated acceleration code, but its unused.", [0], "COL"),
    ("Render priority", "Higher priority in draw queue to improve some transparent elements", [31], "VIS"),
    ("Draw Simple", "Unused, but likely \"ninja simple draw mode\"", [31], "VIS"),
    ("Footprints", "Footprint behavior, only implemented in Emerald Coast", [0], "COL"),
    ("Air", "Barrier/border behavior, usually invisible", [0], "COL"),
    ("Heavy water", "Water flag with heavier physics", [1], "COL"),
    ("Movement-slope-gravity", "Keeps the player stuck to surfaces by altering gravitional direction (?).", [0], "COL"),
    ("No Z-Write", "No Z write, used for shadow/decal meshes", [31], "VIS"),
    ("Draw by mesh", "Sort and draw by mesh, intended to improve self transparency", [31], "VIS"),
    ("No direct", "Landtable entry should not be prebuffered (allows mesh data manipulations)", [31], "VIS"),
    ("Dynamic collision", "Collision should update every frame (for moving tasks)", [0], "COL"),
    ("Dynamic collision rotation", "Collision should rotate with task (ZXY)", [0], "COL"),
    ("Small radius", "Bounds radius is > 10 and < 20 units. If combined with \"Tiny bounds radius\", its >3.", [0, 1], "COL"),
    ("Tiny radius", "Bounds radius is > 3 and < 10 units. If combined with \"Small bounds radius\", its > 3.", [0, 1], "COL"),
    ("Visible", "Enables rendering for the geometry.", None, "VIS")
]

SA2_VISUAL_SURFACE_ATTRIBUTES = [
    None, None, None, None, 
    None, None, None, None,
    None, None, None, None,
    None, None, None,
    ("No shadow", "Surface will not render shadows", [31]),
    None, None, None, None,
    None, None, 
    ("No fog", "Disable fog when rendering", [31]),
    ("Use Sky Draw-distance", "Uses the skybox draw distance instead of the level draw distance", [31]),
    ("Use SimpleDraw", "Use SimpleDraw, else EasyDraw (Dreamcast/Ninja technology)", [31]),
    ("Use DirectDraw", "Use DirectDraw (internal) (Dreamcast/Ninja technology)", [31]),
    ("No compile", "Don't compile model, use other draw", [31]),
    None, None, None, None,
    ("Visible", "Enables rendering for the model")
]

SA2_COLLISION_SURFACE_ATTRIBUTES = [
    ("Solid", "Solid collision"),
    ("Water", "Water flag (ripples, breath counter, heavy physics)"),
    ("Low Friction", "low friction, icy", [0]),
    ("High Friction", "High friction, sticky", [0]),
    ("Medium Friction", "Medium (increased) friction", [0]),
    ("Diggable", "Hunters can dig", [0]),
    None,
    ("Unclimbable", "Surface cannot be climbed by hunters", [0]),
    ("Stairs", "Stairs behavior (upward normal, high floor grip)", [0]),
    None,
    ("Contact damage", "Damages the player on contact.", [0]),
    ("Footprints", "Footprint behavior", [0]),
    ("Cannot land", "Surface will prevent players from standing on it", [0]),
    ("Heavy water", "Heavy water", [1]),
    None, None, None, None,
    None, None,
    ("High Speed", "Top speed increased, faster acceleration", [0]),
    ("High Acceleration", "Faster acceleration, same top speed", [0]),
    ("High Gravity", "Increased gravity above the mesh", [0]),
    None, None, None, None,
    ("DynamicCollision", "Collision should update every frame (for moving tasks)", [0]),
    ("NoRotation", "Do not apply rotation (ZXY) to collision", [0]),
    ("Small radius", "Bounds radius is > 10 and < 20 units. If combined with \"Tiny bounds radius\", its >3.", [0]),
    ("Tiny radius", "Bounds radius is > 3 and < 10 units. If combined with \"Small bounds radius\", its > 3.", [0]),
    None,
]

class SAIO_LevelModel(bpy.types.PropertyGroup):

    geometry_type: EnumProperty(
        name="Type",
        description="Type of the level geometry",
        items=(
            ('STATIC', "Static", "Regular land entry."),
            ('ANIMATED', "Animated", "Aniamted land entry. Not supported by SA2")
        ),
        default='STATIC'
    )

    blockbit: IntProperty(
        name="Blockbit",
        description="bit-flags assigning a model to specific regions (or \"blocks\") in the level",
        subtype="UNSIGNED",
        default=0
    )

    blockbit_hex: StringProperty(
        name="Blockbit (Hexadecimal)",
        description="bit-flags assigning a model to specific regions (or \"blocks\") in the level",
        get=_get_blockbit_hex,
        set=_set_blockbit_hex
    )

    sa1_surface_attributes: IntProperty(
        name="SA1 surface attributes",
        subtype='UNSIGNED',
        default=0
    )

    sa2_visual_surface_attributes: IntProperty(
        name="SA2 visual surface attributes",
        subtype='UNSIGNED',
        default=0
    )

    sa2_collision_surface_attributes: IntProperty(
        name="SA2 collision surface attributes",
        subtype='UNSIGNED',
        default=0
    )

    @classmethod
    def register(cls):
        bpy.types.Object.saio_level_model = PointerProperty(type=cls)

    @classmethod
    def class_setup_attribute_accessors(cls, property, accessors):
        getter_setup = lambda shift: (lambda data: getattr(data, property) & (1 << shift) != 0)
        setter_setup = lambda shift: (lambda data, val: _set_flag(data, property, shift, val))

        for index, attribute in enumerate(accessors):
            if attribute is None:
                attribute = (f"Unknown {index}", "Unknown purpose")

            cls.__annotations__[f"{property[:-1]}_{index}"] = BoolProperty(
                name=attribute[0],
                description=attribute[1],
                get=getter_setup(index),
                set=setter_setup(index)
            )

    @classmethod
    def class_setup(cls):
        cls.class_setup_attribute_accessors("sa1_surface_attributes", SA1_SURFACE_ATTRIBUTES)
        cls.class_setup_attribute_accessors("sa2_visual_surface_attributes", SA2_VISUAL_SURFACE_ATTRIBUTES)
        cls.class_setup_attribute_accessors("sa2_collision_surface_attributes", SA2_COLLISION_SURFACE_ATTRIBUTES)

    @staticmethod
    def evaluate_geometry_type(obj: bpy.types.Object):
        if obj.parent is not None:

            parent = obj.parent
            while parent.parent is not None:
                parent = parent.parent

            if parent.saio_land_entry.geometry_type == 'ANIMATED':
                return (None, "Part of animated object")

            elif parent.type == 'ARMATURE':
                return (None, "Part of an armature object")

            else:
                return ('STATIC', "Child of static geometry")

        elif obj.type == 'ARMATURE':
            return ('ANIMATED', "Object is an armature; Type forced to \"Animated\"")

        elif obj.type not in MESH_DATA_TYPES:
            return (None, 'Does not qualify as a level model: Not a mesh or mesh-like object')

        elif obj.parent is None and len(obj.children) == 0:
            return (obj.saio_level_model.geometry_type, None)

        else:
            return ('STATIC', "Not a root or a child; Type is Static.")
