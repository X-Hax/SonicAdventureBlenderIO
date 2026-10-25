from .scene_properties import SAIO_Scene
from .ginja_material_properties import SAIO_Material_Ginja
from .material_properties import SAIO_Material

to_register = [
    SAIO_Scene,
    SAIO_Material_Ginja,
    SAIO_Material
]