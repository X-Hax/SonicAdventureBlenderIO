from .addon_preferences import SAIO_AddonPreferences
from .scene_properties import SAIO_Scene
from .mesh_properties import SAIO_Mesh
from .ginja_material_properties import SAIO_Material_Ginja
from .material_properties import SAIO_Material
from .node_properties import SAIO_Node

to_register = [
    SAIO_AddonPreferences,
    SAIO_Scene,
    SAIO_Mesh,
    SAIO_Material_Ginja,
    SAIO_Material,
    SAIO_Node
]