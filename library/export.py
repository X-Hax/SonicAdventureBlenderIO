import bpy
from mathutils import Matrix, Vector, Euler
from . import enum, load, mesh
from ..register.property_groups import SAIO_Node


def _evaluate_node_hierarchy(objects: list[bpy.types.Object]):
    # rules:
    # 1. All objects must merge at a root. If there are loose ends,
    # then create a root
    # 2. Children of an armature serve only as mesh carriers.
    # The armatures bones are the real children
    # 3. If an object is part of a hierarchy but not in the list, it
    # will not be exported regardless

    hierarchy_dict: dict[bpy.types.Object, list[bpy.types.Object]] = {}
    parentless: list[bpy.types.Object] = []

    for object in objects:

        parent = object.parent
        while parent is not None and parent not in objects:
            parent = parent.parent

        if parent is not None:
            if parent not in hierarchy_dict:
                hierarchy_dict[parent] = [object]
            else:
                hierarchy_dict[parent].append(object)
        else:
            parentless.append(object)

        if object not in hierarchy_dict:
            hierarchy_dict[object] = []

    return hierarchy_dict, parentless


def _correct_name(name: str):
    underscore = name.find("_")
    if underscore == -1:
        return name

    for i in range(underscore):
        if not name[i].isdigit():
            return name

    return name[:-underscore]


def _create_node_struct(
        name: str,
        matrix: Matrix,
        parent_index: int,
        node_properties: SAIO_Node):

    # conver the name
    name = _correct_name(name)

    # convert node attributes
    from SATools.SAModel.Blender import NodeStruct, Flags

    if node_properties is None:
        node_attributes = Flags.ComposeNodeAttributes(
            False, False, False, False, False, False, False, False)
    else:
        node_attributes = Flags.ComposeNodeAttributes(
            node_properties.ignore_position,
            node_properties.ignore_rotation,
            node_properties.ignore_scale,
            node_properties.rotate_zyx,
            node_properties.skip_draw,
            node_properties.skip_children,
            node_properties.no_animate,
            node_properties.no_morph,
        )

    # correct the matrix
    position, rotation, scale = matrix.decompose()

    new_pos = Vector((position.x, position.z, -position.y))
    new_scale = Vector((scale.x, scale.z, scale.y))

    euler_rotation: Euler = rotation.to_euler('XYZ')
    new_euler_rotation = Euler(
        (euler_rotation.x, euler_rotation.z, -euler_rotation.y))
    new_rotation = new_euler_rotation.to_quaternion()

    new_matrix = Matrix.LocRotScale(new_pos, new_rotation, new_scale)

    return NodeStruct(
        name,
        parent_index,
        node_attributes,
        new_matrix[0][0], new_matrix[1][0], new_matrix[2][0], new_matrix[3][0],
        new_matrix[0][1], new_matrix[1][1], new_matrix[2][1], new_matrix[3][1],
        new_matrix[0][2], new_matrix[1][2], new_matrix[2][2], new_matrix[3][2],
        new_matrix[0][3], new_matrix[1][3], new_matrix[2][3], new_matrix[3][3],
    )


def _evaluate_nodes(objects: list[bpy.types.Object]):

    hierarchy_dict, parentless = _evaluate_node_hierarchy(objects)

    nodes: list = []
    node_mapping: dict[any, int] = {}
    bone_mapping: dict[bpy.types.Object, dict[str, int]] = {}
    virtual_objects: list[tuple[bpy.types.Object, str, bpy.types.Object]] = []

    def add_hierarchy_bone(
            armature_object: bpy.types.Object,
            bone: bpy.types.Bone,
            parent_index: int,
            bone_map: dict[str, int]):

        index = len(nodes)
        matrix_world = armature_object.matrix_world @ bone.matrix_local

        node_mapping[bone] = index
        bone_map[bone.name] = index
        nodes.append(_create_node_struct(
            bone.name,
            matrix_world,
            parent_index,
            bone.saio_node
        ))

        for c in bone.children:
            add_hierarchy_bone(armature_object, c, index, bone_map)

    def add_hierarchy_object(
            object: bpy.types.Object,
            parent_index: int,
            virtual_parent: bpy.types.Object = None,
            virtual_parent_bone: str = None):

        index = len(nodes)
        if virtual_parent is None:
            node_mapping[object] = index
            nodes.append(_create_node_struct(
                object.name,
                object.matrix_world,
                parent_index,
                object.saio_node
            ))

            if object.type == 'ARMATURE':
                bone_map = {}
                for bone in object.data.bones:
                    if bone.parent is None:
                        add_hierarchy_bone(object, bone, index, bone_map)
                bone_mapping[object] = bone_map
                virtual_parent = object
        else:
            if (virtual_parent == object.parent
                    and object.parent_type == 'BONE'):
                virtual_parent_bone = object.parent_bone

            virtual_objects.append(
                (virtual_parent, virtual_parent_bone, object))

        children = hierarchy_dict[object]
        children.sort(key=lambda x: x.name)
        for c in children:
            add_hierarchy_object(c, index, virtual_parent, virtual_parent_bone)

    parentless_index = -1
    if len(parentless) > 1:
        nodes.append(_create_node_struct("root", Matrix.Identity(4), -1, None))
        parentless_index = 0
        parentless.sort(key=lambda x: x.name)

    for p in parentless:
        add_hierarchy_object(p, parentless_index)

    # Returning 3 objects:
    # 1. the node structure in a format that is required by the library
    # 2. object/bone -> node index for mesh root indices
    # 3. armature -> bone name -> node index, for weight indexing
    # 4. virtual objects aka objects that are children of armatures and/or
    # bones and as such only count as model containers. First object is the
    # virtual parent (the armature) and the second the child. Other hierarchial
    # properties are irrelevant and thus ignored

    return nodes, node_mapping, bone_mapping, virtual_objects


def _convert_meshes_to_struct(
        context: bpy.types.Context,
        meshes: list[mesh.ModelMesh],
        apply_modifiers: bool,
        node_count: int,
        bone_mapping: dict[bpy.types.Object, dict[str, int]]):

    for mesh in meshes:
        mesh.prepare_modifiers(apply_modifiers)

    depsgraph = context.evaluated_depsgraph_get()

    mesh_structs = []
    for mesh in meshes:
        mesh.evaluate(depsgraph, apply_modifiers)
        bone_map = None
        if mesh.object.parent in bone_mapping:
            bone_map = bone_mapping[mesh.object.parent]
        weighted_buffer = mesh.convert_to_weighted_buffer(
            context, bone_map, node_count)
        mesh_structs.append(weighted_buffer)

    for mesh in meshes:
        mesh.cleanup_modifiers()

    return mesh_structs


def export_model(
        context: bpy.types.Context,
        objects: list[bpy.types.Object],
        format: str,
        path: str,
        nj_file: bool = False,
        optimize: bool = True,
        ignore_weights: bool = False,
        write_specular: bool = True,
        apply_modifs: bool = True):

    # loading the library
    load.load_library()

    # evaluating node data
    nodes, node_mapping, bone_mapping, virtual_objects \
        = _evaluate_nodes(objects)

    # getting the meshes to convert
    meshes: list[mesh.ModelMesh] = []

    # node meshes
    for node, index in node_mapping.items():
        if not isinstance(node, bpy.types.Object) or node.type != 'MESH':
            continue

        meshes.append(mesh.ModelMesh(node, index))

    # bone/virtual meshes
    for virtual_parent, bone_name, virtual_object in virtual_objects:
        if virtual_object.type != 'MESH':
            continue

        armature = None
        node_index = node_mapping[virtual_parent]

        if bone_name is not None:
            bone_map = bone_mapping[virtual_parent]
            node_index = bone_map[bone_name]
        elif virtual_object.parent == virtual_parent:
            # Virtual parent must be armature.
            # any direct children are probably weighted
            armature = virtual_parent.data

        meshes.append(mesh.ModelMesh(virtual_object, node_index, armature))

    # converting the meshes-
    mesh_structs = _convert_meshes_to_struct(
        context,
        meshes,
        apply_modifs,
        len(nodes),
        bone_mapping
    )

    # exporting
    attach_format = enum.to_attach_format(format)

    from SATools.SAModel.Blender import External

    External.ExportModel(
        nodes,
        mesh_structs,
        attach_format,
        nj_file,
        path,
        optimize,
        ignore_weights,
        write_specular,
        context.scene.saio_scene.author,
        context.scene.saio_scene.description)
