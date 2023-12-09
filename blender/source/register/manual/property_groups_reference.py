NODE = "/ui/object/node/"
LANDENTRY = "ui/object/landentry/"
EVENTENTRY = "ui/object/evententry/"
EVENT_NODE_UI_ANIM = "ui/object/event_node_uv_animations/"
MESH = "/ui/object/mesh/"
MATERIAL = "/ui/object/material/"

SCENE = "/ui/scene/settings/"
LANDTABLE = "/ui/scene/landtable/"
EVENT = "/ui/scene/event/"

TEXTURE = "ui/textures/"
TEXNAME = "ui/texturenames/"

raw_mapping = [
    ("Node.ignore", f"{NODE}#ignore-position-rotation-scale"),
    ("Node.rotate_zyx", f"{NODE}#rotate-zyx"),
    ("Node.skip_draw", f"{NODE}#skip-draw"),
    ("Node.skip_children", f"{NODE}#skip-children"),
    ("Node.no_animate", f"{NODE}#not-animated"),
    ("Node.no_morph", f"{NODE}#no-morph"),

    ("LandEntry.geometry_type", f"{LANDENTRY}#type"),
    ("LandEntry.blockbit", f"{LANDENTRY}#blockbit"),
    ("LandEntry.sf", f"{LANDENTRY}#surface-attributes"),
    ("LandEntry.anim_start_frame", f"{LANDENTRY}#start-frame-offset"),
    ("LandEntry.anim_speed", f"{LANDENTRY}#speed"),
    ("LandEntry.tex_list_pointer", f"{LANDENTRY}#texlist-pointer"),

    ("EventEntry.entry_type", f"{EVENTENTRY}#entry-type"),
    ("EventEntry.shadow_model", f"{EVENTENTRY}#shadow-model"),
    ("EventEntry.reflection", f"{EVENTENTRY}#reflection"),
    ("EventEntry.blare", f"{EVENTENTRY}#blare"),
    ("EventEntry.layer", f"{EVENTENTRY}#layer"),
    ("EventEntry.unk", f"{EVENTENTRY}#unknowns"),
    ("EventEntry.enable_lighting", f"{EVENTENTRY}#enable-lighting"),
    ("EventEntry.disable_shadow_catching", f"{EVENTENTRY}#disable-shadow-catching"),

    ("EventNode_UVAnim.material_index", f"{EVENT_NODE_UI_ANIM}"),

    ("Mesh.force_vertex_colors", f"{MESH}#force-vertex-colors"),
    ("Mesh.texcoord_precision_level", f"{MESH}#texcoord-precision-level"),

    ("Material.diffuse", f"{MATERIAL}#diffuse-color"),
    ("Material.specular", f"{MATERIAL}#specular-color"),
    ("Material.ambient", f"{MATERIAL}#ambient-color"),
    ("Material.specular_exponent", f"{MATERIAL}#specular-strength"),
    ("Material.flat_shading", f"{MATERIAL}#flat-shading"),
    ("Material.ignore", f"{MATERIAL}#ignore-shading-property"),
    ("Material.use_alpha", f"{MATERIAL}#use-alpha"),
    ("Material.double_sided", f"{MATERIAL}#double-sided"),
    ("Material.source_alpha", f"{MATERIAL}#source-destination-alpha"),
    ("Material.destination_alpha", f"{MATERIAL}#source-destination-alpha"),
    ("Material.texture_id", f"{MATERIAL}#texture-id"),
    ("Material.use_texture", f"{MATERIAL}#use-texture"),
    ("Material.use_environment", f"{MATERIAL}#environment-texture"),
    ("Material.texture_filtering", f"{MATERIAL}#texture-filtering"),
    ("Material.anisotropic_filtering", f"{MATERIAL}#anisotropic-filtering"),
    ("Material.mipmap_distance_multiplier", f"{MATERIAL}#mipmap-distance-multiplier"),
    ("Material.clamp", f"{MATERIAL}#uv-sampler"),
    ("Material.mirror", f"{MATERIAL}#uv-sampler"),
    ("Material.shadow_stencil", f"{MATERIAL}#shadow-stencil"),
    ("Material.texgen_coord_id", f"{MATERIAL}#texgen-coord-output-slot"),
    ("Material.texgen_type", f"{MATERIAL}#texgen-type"),
    ("Material.texgen_source", f"{MATERIAL}#texgen-source"),
    ("Material.texgen_matrix_id", f"{MATERIAL}#texgen-matrix-id"),

    ("Scene.author", f"{SCENE}#author"),
    ("Scene.description", f"{SCENE}#description"),
    ("Scene.scene_type", f"{SCENE}#scene-type"),
    ("Scene.use_principled", f"{SCENE}#use-principled-bsdf"),
    ("Scene.light_dir", f"{SCENE}#light-direction"),
    ("Scene.light_color", f"{SCENE}#light-color"),
    ("Scene.light_ambient_color", f"{SCENE}#ambient-color"),
    ("Scene.display_specular", f"{SCENE}#viewport-specular"),
    ("Scene.viewport_alpha", f"{SCENE}#viewport-blend-mode"),
    ("Scene.enable_backface_culling", f"{SCENE}#enable-backface-culling"),

    ("Landtable.name", f"{LANDTABLE}#name"),
    ("Landtable.draw_distance", f"{LANDTABLE}#draw-distance"),
    ("Landtable.double_sided_collision", f"{LANDTABLE}#double-sided-collision"),
    ("Landtable.tex_file_name", f"{LANDTABLE}#texture-filename"),
    ("Landtable.tex_list_pointer", f"{LANDTABLE}#texlist-pointer"),

    ("EventScene.name", f"{EVENT}#event-scenes"),
    ("EventScene.scene", f"{EVENT}#event-scenes"),

    ("OverrideUpgrade.base", f"{EVENT}#base"),
    ("OverrideUpgrade.override", f"{EVENT}#override-1-2"),

    ("AttachUpgrade.model", f"{EVENT}#model-1-2"),
    ("AttachUpgrade.target", f"{EVENT}#target-1-2"),

    ("Event.drop_shadow_control", f"{EVENT}#drop-shadow-control"),
    ("Event.tails_tails", f"{EVENT}#tails-tails"),

    ("Event_UVAnim.texture_index", f"{EVENT}#tex"),
    ("Event_UVAnim.texture_count", f"{EVENT}#num"),

    ("Texture.image", f"{TEXTURE}#image"),
    ("Texture.name", f"{TEXTURE}#slot-name"),
    ("Texture.global_index", f"{TEXTURE}#global-index"),
    ("Texture.override", f"{TEXTURE}#override-resolution"),
    ("Texture.texture_type", f"{TEXTURE}#type"),

    ("Texturename.name", f"{TEXNAME}#texturename-slots-items"),

    ("MaterialMassEdit", "/ui/toolbar/tools/material_mass_edit/")
]

manual_mapping = []
for raw in raw_mapping:
    manual_mapping.append(("bpy.types.saio_" + raw[0].lower() + "*", raw[1]))
