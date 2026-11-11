from .addon_preferences import SAIO_AddonPreferences
from .scene_properties import SAIO_Scene
from .mesh_properties import SAIO_Mesh
from .ginja_material_properties import SAIO_Material_Ginja
from .material_properties import SAIO_Material
from .node_properties import SAIO_Node
from . import texture_properties, texturename_properties

to_register = [

    texture_properties.SAIO_Texture_GV,
    texture_properties.SAIO_Texture_PV,
    texture_properties.SAIO_Texture_PVX,
    texture_properties.SAIO_Texture_PAK,
    texture_properties.SAIO_Texture,
    texture_properties.SAIO_TextureList,

    texturename_properties.SAIO_TextureName,
    texturename_properties.SAIO_TextureNameList,

    SAIO_AddonPreferences,
    SAIO_Scene,
    SAIO_Mesh,
    SAIO_Material_Ginja,
    SAIO_Material,
    SAIO_Node,
]