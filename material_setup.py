import bpy
from . import utils

LIGHTING_PROPERTIES = [
    ("light_ambient_color", "Ambient Color", "NodeSocketColor"),
    ("light_dir", "Light direction", "NodeSocketVector"),
    ("light_color", "Light Color", "NodeSocketColor"),
    ("display_specular", "Specular Factor", "NodeSocketFloat"),
]

MATERIAL_PROPERTIES = {
    "SAIO Shader": [
        ("Use Alpha", "use_alpha", None),
        ("Flat Shading", "flat_shading", None),
        ("Diffuse", "diffuse", None),
        ("Diffuse-Alpha", "diffuse", lambda value: value[3]),
        ("Diffuse Factor", "ignore_diffuse",
            lambda value: 0.0 if value else 1.0),
        ("Specular", "specular", None),
        ("Specular-Alpha", "specular", lambda value: value[3]),
        ("Specular Exponent", "specular_exponent", None),
        ("Specular Factor", "ignore_specular",
            lambda value: 0.0 if value else 1.0),
        ("Ambient", "ambient", None),
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


def _get_node_template() -> bpy.types.NodeTree:

    lib_path = f"{utils.get_path()}\\SAIOShaders.blend"

    found = False
    for library in bpy.data.libraries:
        if library.filepath == lib_path:
            found = True
            break

    if not found:
        bpy.ops.wm.link(
            filename="SAIO Material Template",
            directory=f"{lib_path}\\NodeTree\\"
        )

    # since its possible that previous addon versions were used,
    # we need to absolutely ensure that we return the newest one
    # so we iterate over all of the node groups and check the libraries

    for group in bpy.data.node_groups:
        if (group.name == "SAIO Material Template"
                and group.library is not None
                and group.library.filepath == lib_path):
            return group

    raise Exception("Template not found")


def _get_scene_lighting_node(context: bpy.types.Context):

    node_tree_name = f"SAIO Lighting \"{context.scene.name}\""

    node_tree = bpy.data.node_groups.get(node_tree_name)
    if node_tree is None:
        # set up the node if not exists yet
        node_tree = bpy.data.node_groups.new(node_tree_name, 'ShaderNodeTree')
        node_tree.nodes.new("NodeGroupOutput")

        for property in LIGHTING_PROPERTIES:
            node_tree.outputs.new(property[2], property[1])

    update_scene_lighting(context)

    return node_tree


def _setup_material(
        material: bpy.types.Material,
        template: bpy.types.NodeTree,
        lighting_node_tree: bpy.types.NodeTree):
    '''Clones the template node into the material nodes'''

    mapping = {}
    node_tree = material.node_tree

    # resetting existing contents
    node_tree.links.clear()
    node_tree.nodes.clear()

    def get_socket_by_identifier(sockets, identifier):
        for s in sockets:
            if s.identifier == identifier:
                return s
        return None

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
            input = get_socket_by_identifier(node.inputs, tinput.identifier)
            mapping[tinput] = input
            input.hide = tinput.hide
            if input.type != 'SHADER':
                input.default_value = tinput.default_value

        for toutput in tnode.outputs:
            output = get_socket_by_identifier(node.outputs, toutput.identifier)
            mapping[toutput] = output

    for tlink in template.links:
        from_socket = mapping[tlink.from_socket]
        to_socket = mapping[tlink.to_socket]
        node_tree.links.new(from_socket, to_socket)


def _material_connect_output(
        material: bpy.types.Material,
        use_principled: bool):

    node_tree = material.node_tree

    try:
        output = node_tree.nodes["SAIO Output"]
        shader = node_tree.nodes["SAIO Shader"]
        principled = node_tree.nodes["SAIO Principled"]
    except Exception:
        return

    to_connect = principled if use_principled else shader

    try:
        link = output.inputs[0].links[0]

        if link.from_node == to_connect:
            return

        node_tree.links.remove(link)
    except Exception:
        pass

    node_tree.links.new(to_connect.outputs[0], output.inputs[0])


def _materia_connect_texture(
        material: bpy.types.Material):
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
            for input in inputs:
                node_tree.links.new(texture_output, input)
        else:
            links = []
            for input in inputs:
                for link in input.links:
                    links.append(link)

            for link in links:
                node_tree.links.remove(link)

    setup_links("Texture", "Base Color", 0, use_texture)
    setup_links("Texture-Alpha", "Alpha", 1, use_texture and use_alpha)


def _material_update_blending(
        material: bpy.types.Material,
        blend_method: str,
        clip_threshold: float):

    matprops = material.saio_material
    material.use_backface_culling = matprops.culling

    if not matprops.use_alpha:
        material.blend_method = 'OPAQUE'
        material.shadow_method = 'OPAQUE'
    else:

        material.blend_method = blend_method
        material.alpha_threshold = clip_threshold

        if blend_method == 'BLEND':
            material.shadow_method = 'HASHED'
        else:
            material.shadow_method = blend_method


def update_material_values(
        material: bpy.types.Material,
        blend_method: str,
        clip_threshold: float):
    material_properties = material.saio_material
    node_tree = material.node_tree

    for node_name, properties in MATERIAL_PROPERTIES.items():
        node = node_tree.nodes[node_name]
        for socket_name, prop_name, convert in properties:
            value = getattr(material_properties, prop_name)
            if convert is not None:
                value = convert(value)
            node.inputs[socket_name].default_value = value

    _materia_connect_texture(material)
    _material_update_blending(material, blend_method, clip_threshold)


def update_materials(
        context: bpy.types.Context,
        materials: list[bpy.types.Material]):

    template = _get_node_template()
    lighting_node_tree = _get_scene_lighting_node(context)
    template_nodes = {}

    sceneprops = context.scene.saio_scene
    use_principled = sceneprops.use_principled
    blend_method = sceneprops.viewport_alpha_type
    clip_threshold = sceneprops.viewport_alpha_cutoff

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
        for name, type in template_nodes.items():
            node = node_tree.nodes.get(name)
            if (node is None
                    or node.type != type[0]
                    or (node.type == 'GROUP' and node.node_tree != type[1])):

                _setup_material(material, template, lighting_node_tree)
                break

        _material_connect_output(material, use_principled)
        update_material_values(material, blend_method, clip_threshold)


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
