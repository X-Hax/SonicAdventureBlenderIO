from .addon_preferences import SAIO_AddonPreferences
from .scene_properties import SAIO_Scene
from .mesh_properties import SAIO_Mesh
from .ginja_material_properties import SAIO_Material_Ginja
from .material_properties import SAIO_Material
from .node_properties import SAIO_Node
from . import texturename_properties

to_register = [
    texturename_properties.SAIO_TextureName,
    texturename_properties.SAIO_TextureNameList,

    SAIO_AddonPreferences,
    SAIO_Scene,
    SAIO_Mesh,
    SAIO_Material_Ginja,
    SAIO_Material,
    SAIO_Node,
]