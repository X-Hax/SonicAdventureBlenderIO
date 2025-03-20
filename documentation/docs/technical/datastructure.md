# Python data structure
This is part of the technical documentation, if anyone is interested in messing with the data via scripting. <br/>
A handful of property groups have been added, all of which are documented here. <br/>
The documentation is structured as follows:

```
{Parent type path}
{Parent type path 2}
└─ {Property Name} : {Addon Property Group Type}*
   ├─ [] : {Collection element type}
   │  └─ {{collection element properties}}
   ├─ {Property Name} : {Property Type}
   ├─ {Property Name} : @{Readonly Property Type}
   └─ {Property Name} : {Enum Type}
      └> {Enum Value} : {Display name}
```
---

## Preferences
Addon preferences

<details>
<summary>View</summary>

```
SAIO_AddonPreferences*
├─ auto_check_update : bool
├─ updater_interval_months : int
├─ updater_interval_days  : int
├─ updater_interval_hours  : int
├─ updater_interval_minutes  : int
├─ print_debug : bool
├─ use_project_path : bool
├─ default_path : str
└─ tools_path: str
```
</details>
---

## Scene
Stores per-scene related info and settings

<details>
<summary>View</summary>

```
bpy.types.Scene
└─ saio_scene : SAIO_Scene*
   ├─ author : str
   ├─ description : str
   ├─ scene_type : enum
   │  ├> MDL : Model
   │  ├> LVL : Landtable
   │  ├> EVR : Event root/base scene
   │  └> EVC : Event cut/sub scene
   │
   ├─ use_principled : bool
   ├─ light_dir : vector, tuple[float, float, float]
   ├─ light_color : RGBA, tuple[float, float, float, float]
   ├─ light_ambient : RGBA, tuple[float, float, float, float]
   ├─ display_specular : bool
   ├─ viewport_alpha_cutoff : bool
   │
   ├─ landtable : SAIO_LandTable*
   ├─ event : SAIO_Event*
   ├─ texture_world : bpy.types.World
   ├─ texturename_world : bpy.types.World
   ├─ panels : SAIO_PanelSettings*
   ├─ viewport_panels : SAIO_PanelSettings*
   └─ quick_edit : SAIO_QuickEdit*

```
</details>
---

## Quick Edit
All properties related to the quick edit functionality

<details>
<summary>View</summary>

```
SAIO_Scene*
└─ quick_edit: SAIO_QuickEdit*
    ├─ panels : SAIO_PanelSettings*
	│
    ├─ material_properties : SAIO_Material*
    ├─ use_material_edit : bool
    ├─ apply_diffuse : bool
    ├─ apply_specular : bool
    ├─ apply_ambient : bool
    ├─ apply_specularity : bool
    ├─ apply_texture_id : bool
    ├─ apply_filter : bool
    ├─ apply_mipmap_distance_multiplier : bool
    ├─ apply_source_alpha : bool
    ├─ apply_destination_alpha : bool
    ├─ apply_shadow_stencil : bool
    ├─ apply_texgen_coord_id : bool
    ├─ apply_texgen_type : bool
    ├─ apply_texgen_matrix_id : bool
    ├─ apply_texgen_source : bool
	│
    ├─ land_entry_properties : SAIO_LandEntry*
    ├─ use_land_entry_edit : bool
    ├─ apply_blockbit : bool
	│
    ├─ use_node_edit : bool
    ├─ node_properties : SAIO_Node*
	│
    ├─ use_event_entry_edit : bool
    ├─ apply_entry_type : bool
    ├─ apply_layer : bool
    ├─ event_entry_properties : SAIO_EventEntry*
	│
    ├─ use_mesh_edit : bool
    └─ mesh_properties : SAIO_Mesh*


```
</details>
---

## Panel Settings
Meta properties that are only used for the UI

<details>
<summary>View</summary>

```
SAIO_Scene
├─ panels: SAIO_PanelSettings*
└─ viewport_panels: SAIO_PanelSettings*
   ├─ expanded_material_quick_edit: bool
   ├─ expanded_node_quick_edit: bool
   ├─ expanded_event_entry_quick_edit: bool
   ├─ expanded_land_entry_quick_edit: bool
   ├─ expanded_mesh_quick_edit: bool
   │
   ├─ expanded_texture_properties: bool
   ├─ expanded_rendering_properties: bool
   ├─ expanded_gc_properties: bool
   ├─ expanded_gc_texgen: bool
   │
   ├─ expanded_surface_attributes: bool
   ├─ advanced_surface_attributes: bool
   ├─ land_entry_surface_attributes_editmode: enum
   │  ├> UNIVERSAL : Universal
   │  ├> SA1 : Adventure 1
   │  └> SA2 : Adventure 2
   │
   ├─ expanded_override_upgrade_menu: bool
   ├─ override_upgrade_menu: enum
   │  ├> SONLS : Sonic Light Shoes
   │  ├> SONAL : Sonic Ancient Light
   │  ├> SONMG : Sonic Magic Gloves
   │  ├> SONFR : Sonic Flame Ring
   │  ├> SONBB : Sonic Bounce Bracelet
   │  ├> SONMM : Sonic Mystic Melody
   │  ├> TAIBS : Tails Booster
   │  ├> TAIBZ : Tails Bazooka
   │  ├> TAILB : Tails Laser Blaster
   │  ├> TAIMM : Tails Mystic Melody
   │  ├> KNUSC : Knuckles Shovel Claws
   │  ├> KNUSG : Knuckles Sunglasses
   │  ├> KNUHG : Knuckles Hammer Gloves
   │  ├> KNUAN : Knuckles Air Necklace
   │  ├> KNUMM : Knuckles Mystic Melody
   │  ├> SONSU : Super Sonic
   │  ├> SHAAS : Shadow Air Shoes
   │  ├> SHAAL : Shadow Ancient Light
   │  ├> SHAFR : Shadow Flame Ring
   │  ├> SHAMM : Shadow Mystic Melody
   │  ├> EGGJE : Eggman Jet Engine
   │  ├> EGGLC : Eggman Large Cannon
   │  ├> EGGLB : Eggman Laser Blaster
   │  ├> EGGPA : Eggman Protective Armor
   │  ├> EGGMM : Eggman Mystic Melody
   │  ├> ROUPN : Rouge Pick Nails
   │  ├> ROUTS : Rouge Treasure Scope
   │  ├> ROUIB : Rouge Iron Boots
   │  └> ROUMM : Rouge MysticMelody
   │
   ├─ expanded_attach_upgrade_menu: bool
   ├─ attach_upgrade_menu: enum
   │  ├> SONLS : Sonic Light Shoes
   │  ├> SONFR : Sonic Flame Ring
   │  ├> SONBB : Sonic Bounce Bracelet
   │  ├> SONMG : Sonic Magic Gloves
   │  ├> SHAAS : Shadow Air Shoes
   │  ├> SHAFR : Shadow Flame Ring
   │  ├> KNUS1 : Knuckles Shovel Claws 1
   │  ├> KNUS2 : Knuckles Shovel Claws 2
   │  ├> KNUH1 : Knuckles Hammer Gloves 1
   │  ├> KNUH2 : Knuckles Hammer Gloves 2
   │  ├> KNUSG : Knuckles Sunglasses
   │  ├> KNUAN : Knuckles Air Necklace
   │  ├> ROUPN : Rouge Pick Nails
   │  ├> ROUTS : Rouge Treasure Scope
   │  ├> ROUIB : Rouge Iron Boots
   │  ├> ROUSP : Rouge Shoe Plates (Transparency)
   │  ├> TAIWS : Tails Windshield (Transparency)
   │  └> EGGWS : Eggman Windshield (Transparency)
   │
   ├─ expanded_uv_animations_menu: bool
   │
   ├─ expanded_landtable_panel : bool
   ├─ expanded_texture_panel : bool
   └─ expanded_lighting_panel : bool
```
</details>
---

## Landtable
Stores level info

<details>
<summary>View</summary>

```
SAIO_Scene*
└─ landtable : SAIO_LandTable*
   ├─ name : str
   ├─ draw_distance : int
   ├─ double_sided_collision : bool
   ├─ tex_file_name : str
   └─ tex_list_pointer : str
```
</details>
---

## Event
Stores sa2 root event info

<details>
<summary>View</summary>

```
SAIO_Scene*
└─ event : SAIO_Event*
   ├─ active_index : int
   ├─ [] : SAIO_EventScene*
   │  ├─ name : str
   │  └─ scene : bpy.types.Scene
   │
   ├─ drop_shadow_control : bool
   ├─ tails_tails : bpy.types.Object
   ├─ tails_tails_bone : str
   ├─ uv_animations : SAIO_Event_UVAnimList*
   │  ├─ active_index : int
   │  └─ [] : SAIO_Event_UVAnim*
   │     ├─ texture_index : int
   │     └─ texture_count : int
   │
   ├─ ou_sonls : SAIO_OverrideUpgrade*
   ├─ ou_sonal : SAIO_OverrideUpgrade*
   ├─ ou_sonmg : SAIO_OverrideUpgrade*
   ├─ ou_sonfr : SAIO_OverrideUpgrade*
   ├─ ou_sonbb : SAIO_OverrideUpgrade*
   ├─ ou_sonmm : SAIO_OverrideUpgrade*
   ├─ ou_taibs : SAIO_OverrideUpgrade*
   ├─ ou_taibz : SAIO_OverrideUpgrade*
   ├─ ou_tailb : SAIO_OverrideUpgrade*
   ├─ ou_taimm : SAIO_OverrideUpgrade*
   ├─ ou_knusc : SAIO_OverrideUpgrade*
   ├─ ou_knusg : SAIO_OverrideUpgrade*
   ├─ ou_knuhg : SAIO_OverrideUpgrade*
   ├─ ou_knuan : SAIO_OverrideUpgrade*
   ├─ ou_knumm : SAIO_OverrideUpgrade*
   ├─ ou_sonsu : SAIO_OverrideUpgrade*
   ├─ ou_shaas : SAIO_OverrideUpgrade*
   ├─ ou_shaal : SAIO_OverrideUpgrade*
   ├─ ou_shafr : SAIO_OverrideUpgrade*
   ├─ ou_shamm : SAIO_OverrideUpgrade*
   ├─ ou_eggje : SAIO_OverrideUpgrade*
   ├─ ou_egglc : SAIO_OverrideUpgrade*
   ├─ ou_egglb : SAIO_OverrideUpgrade*
   ├─ ou_eggpa : SAIO_OverrideUpgrade*
   ├─ ou_eggmm : SAIO_OverrideUpgrade*
   ├─ ou_roupn : SAIO_OverrideUpgrade*
   ├─ ou_routs : SAIO_OverrideUpgrade*
   ├─ ou_rouib : SAIO_OverrideUpgrade*
   ├─ ou_roumm : SAIO_OverrideUpgrade*
   ├─ ou_add01 : SAIO_OverrideUpgrade*
   ├─ ou_add02 : SAIO_OverrideUpgrade*
   │  ├─ base : bpy.types.Object
   │  ├─ base_bone : str
   │  ├─ override1 : bpy.types.Object
   │  ├─ override1_bone : str
   │  ├─ override2 : bpy.types.Object
   │  └─ override2_bone : str
   │
   ├─ au_sonls : SAIO_AttachUpgrade*
   ├─ au_sonfr : SAIO_AttachUpgrade*
   ├─ au_sonbb : SAIO_AttachUpgrade*
   ├─ au_sonmg : SAIO_AttachUpgrade*
   ├─ au_shaas : SAIO_AttachUpgrade*
   ├─ au_shafr : SAIO_AttachUpgrade*
   ├─ au_knus1 : SAIO_AttachUpgrade*
   ├─ au_knus2 : SAIO_AttachUpgrade*
   ├─ au_knuh1 : SAIO_AttachUpgrade*
   ├─ au_knuh2 : SAIO_AttachUpgrade*
   ├─ au_knusg : SAIO_AttachUpgrade*
   ├─ au_knuan : SAIO_AttachUpgrade*
   ├─ au_roupn : SAIO_AttachUpgrade*
   ├─ au_routs : SAIO_AttachUpgrade*
   ├─ au_rouib : SAIO_AttachUpgrade*
   ├─ au_rousp : SAIO_AttachUpgrade*
   ├─ au_taiws : SAIO_AttachUpgrade*
   └─ au_eggws : SAIO_AttachUpgrade*
      ├─ model1 : bpy.types.Object
      ├─ target1 : bpy.types.Object
      ├─ target1_bone : str
      ├─ model2 : bpy.types.Object
      ├─ target2 : bpy.types.Object
      └─ target2_bone : str
```
</details>
---

## Texture List
Stores the texture list

<details>
<summary>View</summary>

```
bpy.types.World
└─ saio_texture_list : SAIO_TextureList*
   ├─ active_index : int
   └─ [] : SAIO_Texture*
      ├─ image : bpy.types.Image
	  ├─ name : str
	  ├─ global_index : int
	  ├─ override_width : int
	  ├─ override_width : int
	  ├─ texture_type : enum
	  │  ├> RGBA : Colored
	  │  ├> ID4 : Index4
	  │  └> ID8 : Index8
	  │
	  └─ index : @int
```

Specifically referenced via:
```
bpy.types.Object
└─ saio_texture_world : bpy.types.World

SAIO_Scene*
└─ texture_world : bpy.types.World
```
</details>
---

## Texture Name List
Stores the texture name list

<details>
<summary>View</summary>

```
bpy.types.World
└─ saio_texturename_list
   ├─ active_index : int
   └─ [] : SAIO_TextureName
	  └─ name : str
```

Specifically referenced via:
```
bpy.types.Object
└─ saio_texturename_world : bpy.types.World

SAIO_Scene*
└─ texturename_world : bpy.types.World
```
</details>
---

## Node
Stores node attributes

<details>
<summary>View</summary>

```
bpy.types.Object
bpy.types.EditBone
bpy.types.Bone
└─ saio_node : SAIO_Node*
	├─ ignore_position : bool
	├─ ignore_rotation : bool
	├─ ignore_scale : bool
	├─ rotate_zyx : bool
	├─ skip_draw : bool
	├─ skip_children : bool
	├─ no_animate : bool
	└─ no_morph : bool
```
</details>
---

## Land Entry
Stores surface attributes for level geometry and their blockbit

<details>
<summary>View</summary>

```
bpy.types.Object
└─ saio_land_entry : SAIO_LandEntry*
   ├─ blockbit : str
   │
   ├─ sf_visible : bool
   ├─ sf_solid : bool
   ├─ sf_water : bool
   ├─ sf_water_no_alpha : bool
   │
   ├─ sf_accelerate : bool
   ├─ sf_low_acceleration : bool
   ├─ sf_no_acceleration : bool
   ├─ sf_increased_acceleration : bool
   ├─ sf_tube_acceleration : bool
   ├─ sf_no_friction : bool
   ├─ sf_cannot_land : bool
   ├─ sf_unclimbable : bool
   ├─ sf_stairs : bool
   ├─ sf_diggable : bool
   ├─ sf_hurt : bool
   ├─ sf_dynamic_collision : bool
   ├─ sf_water_collision : bool
   ├─ sf_gravity : bool
   │
   ├─ sf_footprints : bool
   ├─ sf_no_shadows : bool
   ├─ sf_no_fog : bool
   ├─ sf_low_depth : bool
   ├─ sf_use_sky_draw_distance : bool
   ├─ sf_easy_draw : bool
   ├─ sf_no_zwrite : bool
   ├─ sf_draw_by_mesh : bool
   ├─ sf_enable_manipulation : bool
   ├─ sf_waterfall : bool
   ├─ sf_chaos0_land : bool
   ├─ sf_transform_bounds : bool
   ├─ sf_bounds_radius_small : bool
   ├─ sf_bounds_radius_tiny : bool
   │
   ├─ sf_sa1_unknown9 : bool
   ├─ sf_sa1_unknown11 : bool
   ├─ sf_sa1_unknown15 : bool
   ├─ sf_sa1_unknown19 : bool
   │
   ├─ sf_sa2_unknown6 : bool
   ├─ sf_sa2_unknown9 : bool
   ├─ sf_sa2_unknown14 : bool
   ├─ sf_sa2_unknown16 : bool
   ├─ sf_sa2_unknown17 : bool
   ├─ sf_sa2_unknown18 : bool
   ├─ sf_sa2_unknown25 : bool
   └─ sf_sa2_unknown26 : bool
```
</details>
---

## Event Entry
Stores information related to Event entries

<details>
<summary>View</summary>

```
bpy.types.Object
└─ saio_event_entry: SAIO_EventEntry*
   ├─ entry_type : enum
   │  ├> NONE : None
   │  ├> CHUNK : Chunk
   │  ├> GC : GC
   │  ├> SHADOW : GC Shadow
   │  ├> PARTICLE : Particle
   │  └> REFLECTION : Reflection Plane
   │
   ├─ shadow_model : bpy.types.Object
   ├─ reflection : bool
   ├─ blare : bool
   ├─ layer : int
   ├─ unk0 : bool
   ├─ unk2 : bool
   ├─ unk4 : bool
   ├─ unk5 : bool
   ├─ unk6 : bool
   └─ unk9 : bool
```
</details>
---

## Event-Node UV Animation List
Stores per-object specific uv animation info

<details>
<summary>View</summary>

```
bpy.types.Object
└─ saio_eventnode_uvanims : SAIO_EventNode_UVAnimList*
   ├─ active_index : int
   └─ [] : SAIO_EventNode_UVAnim*
      └─ material_index : int
```
</details>
---

## Mesh
Stores mesh specific info

<details>
<summary>View</summary>

```
bpy.types.Mesh
└─ saio_mesh : SAIO_Mesh*
   └─ force_vertex_colors: bool
```
</details>
---

## Material
Stores material settings

<details>
<summary>View</summary>

```
bpy.types.Material
└─ saio_material : SAIO_Material*
   ├─ diffuse : RGBA, tuple[float, float, float, float]
   ├─ specular : RGBA, tuple[float, float, float, float]
   ├─ ambient : RGBA, tuple[float, float, float, float]
   ├─ specular_exponent : int
   ├─ flat_shading : bool
   ├─ ignore_ambient : bool
   ├─ ignore_diffuse : bool
   ├─ ignore_specular : bool
   ├─ use_alpha : bool
   ├─ culling : bool
   │
   ├─ source_alpha : enum
   ├─ destination_alpha : enum
   │  ├> ZERO : Zero
   │  ├> ONE : One
   │  ├> OTHER : Other
   │  ├> INV_OTHER : Inverted other
   │  ├> SRC : Source
   │  ├> INV_SRC : Inverted source
   │  ├> DST : Destination
   │  └> INV_DST : Inverted destination
   │
   ├─ texture_id : int
   ├─ use_texture : bool
   ├─ use_environment : bool
   ├─ texture_filtering :
   ├─ anisotropic_filtering : bool
   ├─ mipmap_distance_multiplier : float
   ├─ clamp_u : bool
   ├─ clamp_v : bool
   ├─ mirror_u : bool
   ├─ mirror_v : bool
   ├─ shadow_stencil : int
   │
   ├─ texgen_coord_id : enum
   │  ├> TEXCOORD0 : TexCoord0
   │  ├> TEXCOORD1 : TexCoord1
   │  ├> TEXCOORD2 : TexCoord2
   │  ├> TEXCOORD3 : TexCoord3
   │  ├> TEXCOORD4 : TexCoord4
   │  ├> TEXCOORD5 : TexCoord5
   │  ├> TEXCOORD6 : TexCoord6
   │  ├> TEXCOORD7 : TexCoord7
   │  ├> TEXCOORDMAX : TexCoordMax
   │  └> TEXCOORDNULL : TexCoordNull
   │
   ├─ texgen_type : enum
   │  ├> MATRIX3X4 : Matrix 3x4
   │  ├> MATRIX2X4 : Matrix 2x4
   │  ├> BITMAP0 : Bitmap 0
   │  ├> BITMAP1 : Bitmap 1
   │  ├> BITMAP2 : Bitmap 2
   │  ├> BITMAP3 : Bitmap 3
   │  ├> BITMAP4 : Bitmap 4
   │  ├> BITMAP5 : Bitmap 5
   │  ├> BITMAP6 : Bitmap 6
   │  ├> BITMAP7 : Bitmap 7
   │  └> SRTG : SRTG
   │
   ├─ texgen_source_matrix : enum
   │  ├> POSITION : Position
   │  ├> NORMAL : Normal
   │  ├> BINORMAL : Binormal
   │  ├> TANGENT : Tangent
   │  ├> TEX0 : Tex0
   │  ├> TEX1 : Tex1
   │  ├> TEX2 : Tex2
   │  ├> TEX3 : Tex3
   │  ├> TEX4 : Tex4
   │  ├> TEX5 : Tex5
   │  ├> TEX6 : Tex6
   │  └> TEX7 : Tex7
   │  ├> TEXCOORD0 : TexCoord0
   │  ├> TEXCOORD1 : TexCoord1
   │  ├> TEXCOORD2 : TexCoord2
   │  ├> TEXCOORD3 : TexCoord3
   │  ├> TEXCOORD4 : TexCoord4
   │  ├> TEXCOORD5 : TexCoord5
   │  └> TEXCOORD6 : TexCoord6
   │  ├> COLOR0 : Color 0
   │  └> COLOR1 : Color 1
   │
   └─ texgen_matrix_id : enum
      ├> MATRIX0 : Matrix 0
      ├> MATRIX1 : Matrix 1
      ├> MATRIX2 : Matrix 2
      ├> MATRIX3 : Matrix 3
      ├> MATRIX4 : Matrix 4
      ├> MATRIX5 : Matrix 5
      ├> MATRIX6 : Matrix 6
      ├> MATRIX7 : Matrix 7
      ├> MATRIX8 : Matrix 8
      ├> MATRIX9 : Matrix 9
      └> IDENTITY : Identity
```
</details>
---

