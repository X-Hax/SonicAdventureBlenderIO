from . import menus
from .scene_panel import SAIO_PT_Scene
from .mesh_panel import SAIO_PT_Mesh
from .material_panel import SAIO_PT_Material
from .node_panel import SAIO_PT_Node, SAIO_PT_Node_Bone

to_register = [
    menus.TOPBAR_MT_SAIO_Import,

    SAIO_PT_Scene,
    SAIO_PT_Mesh,
    SAIO_PT_Material,
    SAIO_PT_Node, 
    SAIO_PT_Node_Bone
]