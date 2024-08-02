import bpy

MIGRATE_KEY = "saio_migrated"
ARMATURE_KEY = "saio_armature_migrated"

ALPHA_MODE = [
    'ZERO', 'ONE', 'OTHER', 'INV_OTHER',
    'SRC', 'INV_SRC', 'DST', 'INV_DST']

TEXFILTER = [
    'NEAREST', 'BILINEAR', 'TRILINEAR', 'BLEND']

TEXGEN_TYPE = [
    'MATRIX3X4', 'MATRIX2X4', 'BUMP0',
    'BUMP1', 'BUMP2', 'BUMP3',
    'BUMP4', 'BUMP5', 'BUMP6',
    'BUMP7', 'SRTG']

TEXGEN_COORD_ID = [
    'TEXCOORD0', 'TEXCOORD1', 'TEXCOORD2',
    'TEXCOORD3', 'TEXCOORD4', 'TEXCOORD5',
    'TEXCOORD6', 'TEXCOORD7', 'TEXCOORDMAX',
    'TEXCOORDNULL']

TEXGEN_SRC_MATRIX = [
    'POSITION', 'NORMAL', 'BINORMAL', 'TANGENT',
    'TEXCOORD0', 'TEXCOORD1', 'TEXCOORD2', 'TEXCOORD3',
    'TEXCOORD4', 'TEXCOORD5', 'TEXCOORD6', 'TEXCOORD7']

TEXGEN_SRC_SRTG = [
    'COLOR0', 'COLOR1']

TEXGEN_SRC_BUMP = [
    'BUMPTEXCOORD0', 'BUMPTEXCOORD1', 'BUMPTEXCOORD2',
    'BUMPTEXCOORD3', 'BUMPTEXCOORD4', 'BUMPTEXCOORD5',
    'BUMPTEXCOORD6']

TEXGEN_MATRIX_ID = [
    'MATRIX0', 'MATRIX1', 'MATRIX2',
    'MATRIX3', 'MATRIX4', 'MATRIX5',
    'MATRIX6', 'MATRIX7', 'MATRIX8',
    'MATRIX9', 'IDENTITY']


class DataHandler:

    def __init__(self, data):
        self.data = data

    def get(self, name, default):
        if name in self.data:
            return self.data[name]
        else:
            return default

    def getb(self, name):
        return self.get(name, False)

    def gets(self, name, default):
        if name in self.data:
            result = self.data[name]
            if len(result) == len(default):
                return result

            sequence = list(result)
            sequence.extend(list(default)[len(result):])
            return sequence
        else:
            return default


def migrate_scene(scene: bpy.types.Scene, remigrate: bool):
    if ("saSettings" not in scene
        or (MIGRATE_KEY in scene
            and not remigrate)):
        return

    data = DataHandler(scene["saSettings"])
    out = scene.saio_scene

    out.author = data.get("author", "")
    out.description = data.get("description", "")
    out.scene_type = 'LVL' if data.get("sceneIsLevel", False) else 'MDL'

    out.light_dir = data.gets("LightDir", (0.0, 0.0, 1.0))
    out.light_color = data.gets("LightColor", (1.0, 1.0, 1.0, 1.0))
    out.light_ambient_color = data.gets(
        "LightAmbientColor", (0.3, 0.3, 0.3, 1.0))
    out.display_specular = data.get("DisplaySpecular", True)

    ltbl = out.landtable
    ltbl.name = data.get("landtableName", "")
    ltbl.draw_distance = data.get("drawDistance", 3000)
    ltbl.double_sided_collision = data.get("doubleSidedCollision", False)
    ltbl.tex_file_name = data.get("texFileName", "")
    ltbl.tex_list_pointer = data.get("texListPointer", "0")

    old_textures = data.get("textureList", [])
    if len(old_textures) > 0:

        out.texture_world = bpy.data.worlds.new(scene.name + " texture list")
        texture_list = out.texture_world.saio_texture_list

        for old_texture in old_textures:
            old_texture = DataHandler(old_texture)

            texture_list.new(
                name=old_texture.get("name", ""),
                global_index=old_texture.get("globalID", 0),
                image=old_texture.get("image", None))

    scene[MIGRATE_KEY] = True


LANDENTRY_MAPPING = {
    "sf_visible" : ["sfVisible", "isVisible"],
    "sf_solid" : ["sfSolid", "solid"],
    "sf_water" : ["sfWater", "sa1_water", "sa2_water", "water"],
    "sf_water_no_alpha" : ["sfWater2", "sa2_water2", "water2"],
    "sf_accelerate" : [("isSA1", "sfAccel"),  "sa1_accelerate"],
    "sf_low_acceleration" : ["sfLowAccel", "sa1_lowAcceleration"],
    "sf_no_acceleration" : ["sfNoAccel", "sa1_noAcceleration", "noAcceleration"],
    "sf_increased_acceleration" : ["sfIncAccel", "sa1_useSkyDrawDistance", "increasedAcceleration"],
    "sf_tube_acceleration" : [("sfAccel", "isSa2"), "sfSA1U_20000"],
    "sf_no_friction" : ["sfNoFriction", "sa1_noFriction", "noFriction"],
    "sf_cannot_land" : ["sfCannotLand", "sa1_cannotLand", "sa2_cannotLand", "cannotLand"],
    "sf_unclimbable" : ["sfUnclimbable", "sa1_unclimbable", "sa2_unclimbable", "unclimbable"],
    "sf_stairs" : ["sfStairs", "sa1_stairs", "sa2_stairs", "standOnSlope"],
    "sf_diggable" : ["sfDiggable", "sa1_diggable", "sa2_diggable", "cannotLand"],
    "sf_hurt" : ["sfHurt", "sa1_hurt", "sa2_hurt", "hurt"],
    "sf_dynamic_collision" : ["sfDynCollision", "sa1_dynCollision"],
    "sf_water_collision" : ["sfWaterCollision", "sa1_colWater"],
    "sf_gravity" : ["sfGravity", "sa1_rotByGravity"],
    "sf_footprints" : ["sfFootprints", "sa1_footprints", "sa2_footprints", "footprints"],
    "sf_no_shadows" : ["sfNoShadows", "sa2_noShadows", "noShadows"],
    "sf_no_fog" : ["sfNoFog", "sa2_noFog", "noFog"],
    "sf_low_depth" : ["sfLowDepth", "sa1_lowDepth"],
    "sf_use_sky_draw_distance" : ["sfUseSkyDrawDistance", "sa1_useSkyDrawDistance"],
    "sf_easy_draw" : ["sfSA2U_1000000", "sa2_unknown24", "unknown24"],
    "sf_no_zwrite" : ["sfNoZWrite", "sa1_noZWrite"],
    "sf_draw_by_mesh" : ["sfDrawByMesh", "sa1_drawByMesh"],
    "sf_enable_manipulation" : ["sfEnableManipulation", "sa1_enableManipulation"],
    "sf_waterfall" : ["sfWaterfall", "sa1_waterfall"],
    "sf_chaos0_land" : ["sfChaos0Land", "sa1_chaos0Land"],
    "sf_transform_bounds" : ["sfUseRotation", "sa1_useRotation"],
    "sf_bounds_radius_small" : ["sfSA1U_20000000", "sfSA2U_20000000", "sa2_unknown29", "unknown29"],
    "sf_bounds_radius_tiny" : ["sfSA1U_40000000", "sfSA2U_40000000", "sa2_unknown30", "unknown30"],

    "sf_sa1_unknown9" : ["sfSA1U_200"],
    "sf_sa1_unknown11" : ["sfSA1U_800"],
    "sf_sa1_unknown15" : ["sfSA1U_8000"],
    "sf_sa1_unknown19" : ["sfSA1U_80000"],
    "sf_sa2_unknown6" : ["sfSA2U_40"],
    "sf_sa2_unknown9" : ["sfSA2U_200"],
    "sf_sa2_unknown14" : ["sfSA2U_4000"],
    "sf_sa2_unknown16" : ["sfSA2U_10000"],
    "sf_sa2_unknown17" : ["sfSA2U_20000"],
    "sf_sa2_unknown18" : ["sfSA2U_40000"],
    "sf_sa2_unknown25" : ["sfSA2U_2000000"],
    "sf_sa2_unknown26" : ["sfSA2U_4000000"],
}

def migrate_landentry(obj: bpy.types.Object, remigrate: bool):
    if ("saSettings" not in obj
        or (MIGRATE_KEY in obj
            and not remigrate)):
        return

    data = DataHandler(obj["saSettings"])
    out = obj.saio_land_entry

    out.blockbit = data.get("blockbit", "0")

    for key, values in LANDENTRY_MAPPING.items():
        flag = False

        for value in values:
            if isinstance(value, str):
                if value in data.data:
                    flag = data.data[value]
                    break
            else:
                value_flag = True
                broke = False
                for value_value in value:
                    if value_value not in data.data:
                        broke = True
                        break
                    value_flag &= data.data[value_value]

                if not broke:
                    flag = value_value
                    break


        setattr(out, key, flag)

    obj[MIGRATE_KEY] = True


def migrate_node(source: bpy.types.Bone | bpy.types.Object, remigrate: bool):
    if ("saObjflags" not in source
        or (MIGRATE_KEY in source
            and not remigrate)):
        return

    data = DataHandler(source["saObjflags"])
    out = source.saio_node

    out.ignore_position = data.getb("ignorePosition")
    out.ignore_rotation = data.getb("ignoreRotation")
    out.ignore_scale = data.getb("ignoreScale")
    out.rotate_zyx = data.getb("rotateZYX")
    out.skip_draw = data.getb("skipDraw")
    out.skip_children = data.getb("skipChildren")
    out.no_animate = data.getb("flagAnimate")
    out.no_morph = data.getb("flagMorph")

    source[MIGRATE_KEY] = True


def migrate_mesh(mesh: bpy.types.Mesh, remigrate: bool):
    if ("saSettings" not in mesh
        or (MIGRATE_KEY in mesh
            and not remigrate)):
        return

    out = mesh.saio_mesh
    data = DataHandler(mesh["saSettings"])

    out.force_vertex_colors = data.get("sa2ExportType", 1) == 0

    mesh[MIGRATE_KEY] = True


def migrate_material(material: bpy.types.Material, remigrate: bool):
    if ("saSettings" not in material
        or (MIGRATE_KEY in material
            and not remigrate)):
        return

    data = DataHandler(material["saSettings"])
    out = material.saio_material

    out.diffuse = data.gets("b_Diffuse", (1.0, 1.0, 1.0, 1.0))
    out.specular = data.gets("b_Specular", (1.0, 1.0, 1.0, 1.0))
    out.ambient = data.gets("b_Ambient", (1.0, 1.0, 1.0, 1.0))
    out.specular_exponent = int(255 * data.get("b_Exponent", 1.0))
    out.flat_shading = data.getb("b_flatShading")
    out.ignore_ambient = data.getb("b_ignoreAmbient")
    out.ignore_diffuse = data.getb("b_ignoreLighting")
    out.ignore_specular = data.getb("b_ignoreSpecular")

    out.use_alpha = data.getb("b_useAlpha")
    out.double_sided = data.getb("b_doubleSided")
    out.source_alpha = ALPHA_MODE[data.get("b_srcAlpha", 4)]
    out.destination_alpha = ALPHA_MODE[data.get("b_destAlpha", 5)]

    out.texture_id = data.get("b_TextureID", 0)
    out.use_texture = data.get("b_useTexture", True)
    out.use_environment = data.getb("b_useEnv")
    out.texture_filtering = TEXFILTER[data.get("b_texFilter", 1)]
    out.anisotropic_filtering = data.getb("b_use_Anisotropy")

    mmdm = 0.25 if data.getb("b_d_025") else 0
    mmdm += 0.5 if data.getb("b_d_050") else 0
    mmdm += 1 if data.getb("b_d_100") else 0
    mmdm += 2 if data.getb("b_d_200") else 0
    out.mipmap_distance_multiplier = mmdm

    out.clamp_u = data.getb("b_clampU")
    out.clamp_v = data.getb("b_clampV")
    out.mirror_u = data.getb("b_mirrorU")
    out.mirror_v = data.getb("b_mirrorV")

    # === GC === #

    out.shadow_stencil = data.get("gc_shadowStencil", 1)
    out.texgen_coord_id = TEXGEN_COORD_ID[data.get("gc_texCoordID", 0)]
    out.texgen_type = TEXGEN_TYPE[data.get("gc_texGenType", 1)]
    out.texgen_matrix_id = TEXGEN_MATRIX_ID[data.get("gc_texMatrixID", 10)]

    if out.texgen_type[0] == 'M':
        out.texgen_source = TEXGEN_SRC_MATRIX[
            data.get("gc_texGenSourceMtx", 5)]
    elif out.texgen_type[0] == 'B':
        out.texgen_source = TEXGEN_SRC_BUMP[
            data.get("gc_texGenSourceBmp", 0)]
    else:
        out.texgen_source = TEXGEN_SRC_SRTG[
            data.get("gc_texGenSourceSRTG", 0)]

    material[MIGRATE_KEY] = True


def migrate_file(remigrate: bool):
    for scene in bpy.data.scenes:
        migrate_scene(scene, remigrate)

    for object in bpy.data.objects:
        migrate_landentry(object, remigrate)
        migrate_node(object, remigrate)

    for armature in bpy.data.armatures:
        for bone in armature.bones:
            migrate_node(bone, remigrate)

    for mesh in bpy.data.meshes:
        migrate_mesh(mesh, remigrate)

    for material in bpy.data.materials:
        migrate_material(material, remigrate)
