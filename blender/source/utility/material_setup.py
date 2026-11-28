import bpy
from ..exceptions import SAIOException
from . import general, texture_manager

MATERIAL_PROPERTIES = {
    "SAIO Principled": [
        ("Base Color", "diffuse", None),
        ("Roughness", "specular_exponent", lambda value: 1.0 - (value / 255.0)),
    ],
    "SAIO UV": [
        ("Mirror U", "mirror_u", None),
        ("Mirror V", "mirror_v", None),
        ("Clamp U", "clamp_u", None),
        ("Clamp V", "clamp_v", None),
        ("Environment Mapping", "texturing_mode", lambda value: value == 'ENV'),
    ]
}

def _get_node_template() -> bpy.types.Material:
    general.load_template_blend()

    # since its possible that previous addon versions were used,
    # we need to absolutely ensure that we return the newest one
    # so we iterate over all of the node groups and check the libraries

    for group in bpy.data.node_groups:
        if (group.name.startswith("SAIO Material Template")
                and general.is_from_template(group)):
            return group

    raise SAIOException("Template not found")

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
        template: bpy.types.NodeTree):
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
        node.hide = tnode.hide

        if tnode.type == 'GROUP':
            node.node_tree = tnode.node_tree

        elif tnode.type == 'MIX':
            node.data_type = tnode.data_type
            node.blend_type = tnode.blend_type

        elif tnode.type == 'MATH':
            node.operation = tnode.operation

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

###############################################################################

def get_texture_node(material: bpy.types.Material) -> bpy.types.ShaderNodeTexImage | None:
    if (material.node_tree is None or "SAIO Texture" not in material.node_tree.nodes):
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

    if (texture_list is None or index >= len(texture_list.textures)):
        texture_node.image = None
    elif texture_list.textures[index] is not None:
        texture_node.image = texture_list.textures[index].image
    else:
        texture_node.image = None


def _material_connect_texture(
        material: bpy.types.Material):

    if not material.use_nodes:
        return

    use_texture = material.saio_material.use_texture
    use_alpha = material.saio_material.alpha_mode != 'OPAQUE'
    node_tree = material.node_tree

    try:
        texture = node_tree.nodes["SAIO Texture"]
        shader = node_tree.nodes["SAIO Principled"]
        color = node_tree.nodes["SAIO Color"]
    except Exception:
        return

    def setup_links(
            output_index: int,
            input_node: bpy.types.ShaderNode,
            input_name: str,
            use_link: bool):

        texture_output = texture.outputs[output_index]
        input_socket = input_node.inputs[input_name]

        if use_link:
            node_tree.links.new(texture_output, input_socket)
        else:
            links = list(input_socket.links)
            for link in links:
                node_tree.links.remove(link)

    setup_links(0, color, "B", use_texture)
    setup_links(1, shader, "Alpha", use_texture and use_alpha)


def _material_update_blending(material: bpy.types.Material):
    material.use_backface_culling = not material.saio_material.double_sided
    material.use_backface_culling_shadow = material.use_backface_culling
    material.surface_render_method = 'DITHERED'
    material.use_transparent_shadow = False

###############################################################################

def update_material_values(material: bpy.types.Material):

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
    _material_update_blending(material)

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

    template = _get_node_template()
    template_nodes = {}

    texlist_manager = texture_manager.TexlistManager()
    texlist_manager.evaluate_texlists(context.scene)

    for node in template.nodes:
        node_tree = None
        if node.type == 'GROUP':
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

                _setup_material(material, template)
                _update_material_texture(texlist_manager, material)
                break

        update_material_values(material)


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
