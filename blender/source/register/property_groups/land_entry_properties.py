import bpy
from bpy.props import (
    BoolProperty,
    StringProperty,
    PointerProperty
)


class SAIO_LandEntry(bpy.types.PropertyGroup):
    """Property Group for managing Land Entry surface flags"""

    blockbit: StringProperty(
        name="Blockbit (hex)",
        description="BitFlags for LandEntry Objects",
        default="0"
    )

    # ===== Surface Attributes =====

    sf_visible: BoolProperty(
        name="Visible",
        default=True
    )

    sf_solid: BoolProperty(
        name="Solid",
        default=False
    )

    sf_water: BoolProperty(
        name="Water",
        default=False
    )

    sf_water_no_alpha: BoolProperty(
        name="Water No Alpha",
        default=False
    )

    sf_accelerate: BoolProperty(
        name="Accelerate",
        default=False
    )

    sf_low_acceleration: BoolProperty(
        name="Low Acceleration",
        default=False
    )

    sf_no_acceleration: BoolProperty(
        name="No Acceleration",
        default=False
    )

    sf_increased_acceleration: BoolProperty(
        name="Increased Acceleration",
        default=False
    )

    sf_tube_acceleration: BoolProperty(
        name="Tube Acceleration",
        default=False
    )

    sf_no_friction: BoolProperty(
        name="No Friction",
        default=False
    )

    sf_cannot_land: BoolProperty(
        name="Cannot Land",
        default=False
    )

    sf_unclimbable: BoolProperty(
        name="Unclimbable",
        default=False
    )

    sf_stairs: BoolProperty(
        name="Stairs",
        default=False
    )

    sf_diggable: BoolProperty(
        name="Diggable",
        default=False
    )

    sf_hurt: BoolProperty(
        name="Hurt",
        default=False
    )

    sf_dynamic_collision: BoolProperty(
        name="Dynamic Collision",
        default=False
    )

    sf_water_collision: BoolProperty(
        name="Water Collision",
        default=False
    )

    sf_gravity: BoolProperty(
        name="Gravity",
        default=False
    )

    sf_footprints: BoolProperty(
        name="Footprints",
        default=False
    )

    sf_no_shadows: BoolProperty(
        name="No Shadows",
        default=False
    )

    sf_no_fog: BoolProperty(
        name="No Fog",
        default=False
    )

    sf_low_depth: BoolProperty(
        name="Low Depth",
        default=False
    )

    sf_use_sky_draw_distance: BoolProperty(
        name="Use Sky Draw Distance",
        default=False
    )

    sf_easy_draw: BoolProperty(
        name="Easy Draw",
        default=False
    )

    sf_no_zwrite: BoolProperty(
        name="No ZWrite",
        default=False
    )

    sf_draw_by_mesh: BoolProperty(
        name="Draw By Mesh",
        default=False
    )

    sf_enable_manipulation: BoolProperty(
        name="Enable Manipulation",
        default=False
    )

    sf_waterfall: BoolProperty(
        name="Waterfall",
        default=False
    )

    sf_chaos0_land: BoolProperty(
        name="Chaos0 Land",
        default=False
    )

    sf_transform_bounds: BoolProperty(
        name="Transform Bounds",
        default=False
    )

    sf_bounds_radius_small: BoolProperty(
        name="Bounds Radius Small",
        default=False
    )

    sf_bounds_radius_tiny: BoolProperty(
        name="Bounds Radius Tiny",
        default=False
    )

    sf_sa1_unknown9: BoolProperty(
        name="SA1 Unknown9",
        default=False
    )

    sf_sa1_unknown11: BoolProperty(
        name="SA1 Unknown11",
        default=False
    )

    sf_sa1_unknown15: BoolProperty(
        name="SA1 Unknown15",
        default=False
    )

    sf_sa1_unknown19: BoolProperty(
        name="SA1 Unknown19",
        default=False
    )

    sf_sa2_unknown6: BoolProperty(
        name="SA2 Unknown6",
        default=False
    )

    sf_sa2_unknown9: BoolProperty(
        name="SA2 Unknown9",
        default=False
    )

    sf_sa2_unknown14: BoolProperty(
        name="SA2 Unknown14",
        default=False
    )

    sf_sa2_unknown16: BoolProperty(
        name="SA2 Unknown16",
        default=False
    )

    sf_sa2_unknown17: BoolProperty(
        name="SA2 Unknown17",
        default=False
    )

    sf_sa2_unknown18: BoolProperty(
        name="SA2 Unknown18",
        default=False
    )

    sf_sa2_unknown25: BoolProperty(
        name="SA2 Unknown25",
        default=False
    )

    sf_sa2_unknown26: BoolProperty(
        name="SA2 Unknown26",
        default=False
    )

    @property
    def is_visual(self):
        return self.sf_visible

    @property
    def is_collision(self):
        return (
            self.sf_solid
            or self.sf_water
            or self.sf_water_no_alpha
        )

    @classmethod
    def register(cls):
        bpy.types.Object.saio_land_entry = PointerProperty(type=cls) # pylint: disable=assignment-from-no-return

    @staticmethod
    def check_is_land_entry(obj: bpy.types.Object):
        if obj.type != 'MESH':
            return "Object is not a mesh"

        return None
