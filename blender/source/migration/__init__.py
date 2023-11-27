import bpy

MIGRATE_KEY = "saio_migrated"
ARMATURE_KEY = "saio_armature_migrated"

VIEWPORT_ALPHA_TYPE = [
    'BLEND', 'HASHED', 'CLIP']

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
    out.viewport_alpha_type = VIEWPORT_ALPHA_TYPE[data.get(
        "viewportAlphaType", 0)]
    out.viewport_alpha_cutoff = data.get("viewportAlphaCutoff", 0.5)

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


def migrate_landentry(obj: bpy.types.Object, remigrate: bool):
    if ("saSettings" not in obj
        or (MIGRATE_KEY in obj
            and not remigrate)):
        return

    data = DataHandler(obj["saSettings"])
    out = obj.saio_land_entry

    out.blockbit = data.get("blockbit", "0")

    out.sf_visible = data.getb("sfVisible")
    out.sf_solid = data.getb("sfSolid")
    out.sf_water = data.getb("sfWater")
    out.sf_water_no_alpha = data.getb("sfWater2")
    out.sf_accelerate = data.getb("isSA1") and data.getb("sfAccel")
    out.sf_low_acceleration = data.getb("sfLowAccel")
    out.sf_no_acceleration = data.getb("sfNoAccel")
    out.sf_increased_acceleration = data.getb("sfIncAccel")

    out.sf_tube_acceleration = (
        (data.getb("sfAccel") and data.getb("isSa2"))
        or data.getb("sfSA1U_20000"))

    out.sf_no_friction = data.getb("sfNoFriction")
    out.sf_cannot_land = data.getb("sfCannotLand")
    out.sf_unclimbable = data.getb("sfUnclimbable")
    out.sf_stairs = data.getb("sfStairs")
    out.sf_diggable = data.getb("sfDiggable")
    out.sf_hurt = data.getb("sfHurt")
    out.sf_dynamic_collision = data.getb("sfDynCollision")
    out.sf_water_collision = data.getb("sfWaterCollision")
    out.sf_gravity = data.getb("sfGravity")
    out.sf_footprints = data.getb("sfFootprints")
    out.sf_no_shadows = data.getb("sfNoShadows")
    out.sf_no_fog = data.getb("sfNoFog")
    out.sf_low_depth = data.getb("sfLowDepth")
    out.sf_use_sky_draw_distance = data.getb("sfUseSkyDrawDistance")
    out.sf_easy_draw = data.getb("sfSA2U_1000000")
    out.sf_no_zwrite = data.getb("sfNoZWrite")
    out.sf_draw_by_mesh = data.getb("sfDrawByMesh")
    out.sf_enable_manipulation = data.getb("sfEnableManipulation")
    out.sf_waterfall = data.getb("sfWaterfall")
    out.sf_chaos0_land = data.getb("sfChaos0Land")
    out.sf_transform_bounds = data.getb("sfUseRotation")

    out.sf_bounds_radius_small = \
        data.getb("sfSA1U_20000000") or data.getb("sfSA2U_20000000")
    out.sf_bounds_radius_tiny = \
        data.getb("sfSA1U_40000000") or data.getb("sfSA2U_40000000")

    out.sf_sa1_unknown9 = data.getb("sfSA1U_200")
    out.sf_sa1_unknown11 = data.getb("sfSA1U_800")
    out.sf_sa1_unknown15 = data.getb("sfSA1U_8000")
    out.sf_sa1_unknown19 = data.getb("sfSA1U_80000")
    out.sf_sa2_unknown6 = data.getb("sfSA2U_40")
    out.sf_sa2_unknown9 = data.getb("sfSA2U_200")
    out.sf_sa2_unknown14 = data.getb("sfSA2U_4000")
    out.sf_sa2_unknown16 = data.getb("sfSA2U_10000")
    out.sf_sa2_unknown17 = data.getb("sfSA2U_20000")
    out.sf_sa2_unknown18 = data.getb("sfSA2U_40000")
    out.sf_sa2_unknown25 = data.getb("sfSA2U_2000000")
    out.sf_sa2_unknown26 = data.getb("sfSA2U_4000000")

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
