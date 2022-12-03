"""All property groups declared by the addon"""

from .panel_properties import SAIO_PanelSettings
from .land_entry_properties import SAIO_LandEntry
from .material_properties import SAIO_Material
from .mesh_properties import SAIO_Mesh
from .node_properties import SAIO_Node
from .project_properties import SAIO_Project
from .texture_properties import SAIO_Texture
from .landtable_properties import SAIO_LandTable
from .quick_edit_properties import SAIO_QuickEdit
from .scene_properties import SAIO_Scene
from .addon_preferences import SAIO_AddonPreferences

# Order is important
to_register = [
    SAIO_PanelSettings,
    SAIO_LandEntry,
    SAIO_Material,
    SAIO_Mesh,
    SAIO_Node,
    SAIO_Project,
    SAIO_Texture,
    SAIO_LandTable,

    SAIO_QuickEdit,
    SAIO_Scene,

    SAIO_AddonPreferences
]
