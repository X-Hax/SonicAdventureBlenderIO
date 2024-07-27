import bpy
from . import texture_manager, general
from ..exceptions import SAIOException

LIGHTING_PROPERTIES = [
    ("light_ambient_color", "Ambient Color", "NodeSocketColor"),
    ("light_dir", "Light direction", "NodeSocketVector"),
    ("light_color", "Light Color", "NodeSocketColor"),
    ("display_specular", "Specular Factor", "NodeSocketFloat"),
]


def _convert_to_gamma(color):
    return (
        color[0] ** 2,
        color[1] ** 2,
        color[2] ** 2,
        color[3],
    )


MATERIAL_PROPERTIES = {
    "SAIO Shader": [
        ("Use Alpha", "use_alpha", None),
        ("Flat Shading", "flat_shading", None),
        ("Diffuse", "diffuse", _convert_to_gamma),
        ("Diffuse-Alpha", "diffuse", lambda value: value[3]),
        ("Lighting Factor", "ignore_diffuse",
            lambda value: 0.0 if value else 1.0),
        ("Specular", "specular", _convert_to_gamma),
        ("Specular-Alpha", "specular", lambda value: value[3]),
        ("Specular Exponent", "specular_exponent", None),
        ("Specular Factor", "ignore_specular",
            lambda value: 0.0 if value else 1.0),
        ("Ambient", "ambient", _convert_to_gamma),
        ("Ambient-Alpha", "ambient", lambda value: value[3]),
        ("Ambient Factor", "ignore_ambient",
            lambda value: 0.0 if value else 1.0),
    ],
    "SAIO Principled": [
        ("Base Color", "diffuse", None),
        ("Roughness", "specular_exponent",
            lambda value: 1.0 - (value / 255.0)),
    ],
    "SAIO UV": [
        ("Mirror U", "mirror_u", None),
        ("Mirror V", "mirror_v", None),
        ("Clamp U", "clamp_u", None),
        ("Clamp V", "clamp_v", None),
        ("Env Mapping", "use_environment", None),
    ]
}


def _get_node_template(context: bpy.types.Context) -> bpy.types.NodeTree:
    general.load_template_blend(context)

    # since its possible that previous addon versions were used,
    # we need to absolutely ensure that we return the newest one
    # so we iterate over all of the node groups and check the libraries

    for group in bpy.data.node_groups:
        if (group.name.startswith("SAIO Material Template")
                and general.is_from_template(group)):
            return group

    raise SAIOException("Template not found")


def _get_scene_lighting_node(context: bpy.types.Context):

    node_tree_name = f"SAIO Lighting \"{context.scene.name}\""

    node_tree = bpy.data.node_groups.get(node_tree_name)
    if node_tree is None:
        # set up the node if not exists yet
        node_tree = bpy.data.node_groups.new(node_tree_name, 'ShaderNodeTree')
        node_tree.nodes.new("NodeGroupOutput")

        for prop in LIGHTING_PROPERTIES:
            node_tree.interface.new_socket(
                in_out='OUTPUT',
                name=prop[1],
                socket_type=prop[2]
            )

    update_scene_lighting(context)

    return node_tree

###############################################################################

def _get_socket_by_identifier(
        sockets: list[bpy.types.NodeSocket],
        identifier: str) -> bpy.types.NodeSocket:

    for item in sockets:
        if item.identifier == identifier:
            return item
    return None


def _setup_material(
        material: bpy.types.Material,
        template: bpy.types.NodeTree,
        lighting_node_tree: bpy.types.NodeTree):
    '''Clones the template node into the material nodes'''

    if not material.use_nodes:
        return

    mapping = {}
    node_tree = material.node_tree
    material.preview_render_type = 'FLAT'

    # resetting existing contents
    node_tree.links.clear()
    node_tree.nodes.clear()

    for tnode in template.nodes:
        node = node_tree.nodes.new(tnode.bl_idname)
        mapping[tnode] = node

        node.name = tnode.name
        node.label = tnode.label
        node.height = tnode.height
        node.width = tnode.width
        node.location = tnode.location

        if tnode.type == 'GROUP':
            if tnode.name == 'SAIO Lighting':
                node.node_tree = lighting_node_tree
            else:
                node.node_tree = tnode.node_tree

        for tinput in tnode.inputs:
            input_socket = _get_socket_by_identifier(node.inputs, tinput.identifier)
            mapping[tinput] = input_socket
            input_socket.hide = tinput.hide
            if input_socket.type != 'SHADER':
                input_socket.default_value = tinput.default_value

        for toutput in tnode.outputs:
            output = _get_socket_by_identifier(node.outputs, toutput.identifier)
            mapping[toutput] = output

    for tlink in template.links:
        from_socket = mapping[tlink.from_socket]
        to_socket = mapping[tlink.to_socket]
        node_tree.links.new(from_socket, to_socket)


def _material_connect_output(
        material: bpy.types.Material,
        use_principled: bool):

    if not material.use_nodes:
        return

    node_tree = material.node_tree

    try:
        output = node_tree.nodes["SAIO Output"]
        shader = node_tree.nodes["SAIO Shader"]
        principled = node_tree.nodes["SAIO Principled"]
    except Exception:
        return

    to_connect = principled if use_principled else shader

    try:
        link: bpy.types.NodeLink = output.inputs[0].links[0]

        if link.from_node == to_connect:
            return

        node_tree.links.remove(link)
    except Exception:
        pass

    node_tree.links.new(to_connect.outputs[0], output.inputs[0])


def _material_connect_texture(
        material: bpy.types.Material):

    if not material.use_nodes:
        return

    use_texture = material.saio_material.use_texture
    use_alpha = material.saio_material.use_alpha
    node_tree = material.node_tree

    try:
        texture = node_tree.nodes["SAIO Texture"]
        shader = node_tree.nodes["SAIO Shader"]
        principled = node_tree.nodes["SAIO Principled"]
    except Exception:
        return

    def setup_links(
            shader_input: str,
            principled_input: str,
            output_index: int,
            use_link: bool):

        inputs = [
            shader.inputs[shader_input],
            principled.inputs[principled_input],
        ]

        texture_output = texture.outputs[output_index]

        if use_link:
            for input_socket in inputs:
                node_tree.links.new(texture_output, input_socket)
        else:
            links = []
            for input_socket in inputs:
                for link in input_socket.links:
                    links.append(link)

            for link in links:
                node_tree.links.remove(link)

    setup_links("Texture", "Base Color", 0, use_texture)
    setup_links("Texture-Alpha", "Alpha", 1, use_texture and use_alpha)


def _material_update_blending(
        material: bpy.types.Material,
        enable_backface_culling: bool):

    matprops = material.saio_material
    material.use_backface_culling = (
        not matprops.double_sided and enable_backface_culling
    )
    material.use_backface_culling_shadow = material.use_backface_culling

    material.surface_render_method = 'DITHERED'
    material.use_transparent_shadow = False

###############################################################################


def update_material_values(
        material: bpy.types.Material,
        enable_backface_culling: bool):

    material_properties = material.saio_material

    material.diffuse_color = (
        material_properties.diffuse[0],
        material_properties.diffuse[1],
        material_properties.diffuse[2],
        1,
    )
    material.metallic = 0
    material.roughness = 1 - (material_properties.specular_exponent / 255.0)

    if not material.use_nodes:
        return

    node_tree = material.node_tree

    for node_name, properties in MATERIAL_PROPERTIES.items():
        try:
            node = node_tree.nodes[node_name]
        except KeyError:
            return

        for socket_name, prop_name, convert in properties:
            value = getattr(material_properties, prop_name)
            if convert is not None:
                value = convert(value)
            node.inputs[socket_name].default_value = value

    _material_connect_texture(material)
    _material_update_blending(
        material, enable_backface_culling)


def update_material_outputs(
        materials: list[bpy.types.Material],
        use_principled: bool):

    for material in materials:
        _material_connect_output(material, use_principled)


def update_scene_lighting(context: bpy.types.Context):
    '''Updates the lighting group values to that of the scene'''

    node_tree_name = f"SAIO Lighting \"{context.scene.name}\""
    node_tree = bpy.data.node_groups.get(node_tree_name)
    if node_tree is None:
        return

    group_out = node_tree.nodes[0]
    scene_properties = context.scene.saio_scene

    for prop in LIGHTING_PROPERTIES:
        value = getattr(scene_properties, prop[0])
        group_out.inputs[prop[1]].default_value = value

###############################################################################


def get_texture_node(material) -> bpy.types.ShaderNodeTexImage | None:
    if (material.node_tree is None
            or "SAIO Texture" not in material.node_tree.nodes):
        return None
    return material.node_tree.nodes["SAIO Texture"]


def _update_material_texture(
        texlist_manager: texture_manager.TexlistManager,
        material: bpy.types.Material):

    texture_node = get_texture_node(material)
    if texture_node is None:
        return

    index = material.saio_material.texture_id
    texture_list = texlist_manager.get_material_texlist(material)

    if (texture_list is None
            or index >= len(texture_list.textures)):
        texture_node.image = None
    elif texture_list.textures[index] is not None:
        texture_node.image = texture_list.textures[index].image
    else:
        texture_node.image = None


def update_material_textures(
        context: bpy.types.Context,
        materials: list[bpy.types.Material]):

    texlist_manager = texture_manager.TexlistManager()
    texlist_manager.evaluate_texlists(context.scene)

    for material in materials:
        _update_material_texture(texlist_manager, material)


def _update_material_texid(
        texlist_manager: texture_manager.TexlistManager,
        material: bpy.types.Material):

    texture_node = get_texture_node(material)
    if texture_node is None or texture_node.image is None:
        return

    texture_list = texlist_manager.get_material_texlist(material)
    if texture_list is None:
        return

    index = texture_list.get_index(texture_node.image)
    if index is not None:
        material.saio_material.texture_id = index


def update_material_texids(
        context: bpy.types.Context,
        materials: list[bpy.types.Material]):

    texlist_manager = texture_manager.TexlistManager()
    texlist_manager.evaluate_texlists(context.scene)

    for material in materials:
        _update_material_texid(texlist_manager, material)

###############################################################################


def setup_and_update_materials(
        context: bpy.types.Context,
        materials: list[bpy.types.Material]):

    template = _get_node_template(context)
    lighting_node_tree = _get_scene_lighting_node(context)
    template_nodes = {}

    sceneprops = context.scene.saio_scene
    use_principled = sceneprops.use_principled
    enable_backface_culling = sceneprops.enable_backface_culling

    texlist_manager = texture_manager.TexlistManager()
    texlist_manager.evaluate_texlists(context.scene)

    for node in template.nodes:
        node_tree = None
        if node.type == 'GROUP':
            if node.name == 'SAIO Lighting':
                node_tree = lighting_node_tree
            else:
                node_tree = node.node_tree

        template_nodes[node.name] = (node.type, node_tree)

    for material in materials:
        material.use_nodes = True
        node_tree = material.node_tree

        # validate that the nodes exist
        for name, tree in template_nodes.items():
            node = node_tree.nodes.get(name)
            if (node is None
                    or node.type != tree[0]
                    or (node.type == 'GROUP' and node.node_tree != tree[1])):

                _setup_material(material, template, lighting_node_tree)
                _update_material_texture(texlist_manager, material)
                break

        _material_connect_output(material, use_principled)
        update_material_values(material, enable_backface_culling)


def assemble_texture_list(
        materials: set[bpy.types.Material],
        global_index_offset: int):

    texs = set()
    for mat in materials:
        texture = get_texture_node(mat)
        if texture is not None and texture.image is not None:
            texs.add(texture.image)

    world = bpy.data.worlds.new("auto_texlist")
    texlist = world.saio_texture_list

    texs = list(texs)
    texs.sort(key=lambda x: x.name.lower())
    index = global_index_offset
    for tex in texs:
        item = texlist.new(image=tex)
        item.global_index = index
        index += 1

    return world
