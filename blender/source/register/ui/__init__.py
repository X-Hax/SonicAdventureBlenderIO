from . import menus
from .scene_panel import SAIO_PT_Scene
from .mesh_panel import SAIO_PT_Mesh
from .material_panel import SAIO_PT_Material
from .node_panel import SAIO_PT_Node, SAIO_PT_Node_Bone
from . import texturename_panel, texture_panel

to_register = [
    menus.TOPBAR_MT_SAIO_Import,

    SAIO_PT_Scene,
    SAIO_PT_Mesh,
    SAIO_PT_Material,
    SAIO_PT_Node, 
    SAIO_PT_Node_Bone,

    texture_panel.SAIO_UL_TextureList,
    texture_panel.SAIO_MT_TextureContextMenuScene,
    texture_panel.SAIO_MT_TextureContextMenuObject,
    texture_panel.SAIO_PT_SceneTextures,
    texture_panel.SAIO_PT_ObjectTextures,

    texturename_panel.SAIO_UL_TextureNameList,
    texturename_panel.SAIO_MT_TextureNameContextMenuScene,
    texturename_panel.SAIO_MT_TextureNameContextMenuObject,
    texturename_panel.SAIO_PT_SceneTexturenames,
    texturename_panel.SAIO_PT_ObjectTexturenames,
]