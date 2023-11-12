from .system import System
from .textcopy import TextCopy
from .sa3d_common import SA3D_Common
from .sa3d_texturing import SA3D_Texturing
from .sa3d_archival import SA3D_Archival
from .sa3d_modeling import SA3D_Modeling
from .sa3d_sa2event import SA3D_SA2Event
from .saio_net import SAIO_NET

from ..utility.general import get_path
from ..exceptions import UserException

_LOADED = False

LIBRARIES = [
    System,
    TextCopy,
    SA3D_Common,
    SA3D_Texturing,
    SA3D_Archival,
    SA3D_Modeling,
    SA3D_SA2Event,
    SAIO_NET,
]

def load_dotnet():
    global _LOADED
    if _LOADED:
        return

    try:
        import pythonnet
    except ModuleNotFoundError as exc:
        raise UserException((
            "Could not install python.net, please try running blender with"
            " admin rights")) from exc

    path = get_path() + "\\DLL\\"
    dll_paths = [
        "SAIO.NET.dll",
        "SA3D.Archival.dll",
        "TextCopy.dll",
    ]

    runtime_config = f"{path}SAIO.NET.runtimeconfig.json"

    import pythonnet
    pythonnet.load("coreclr", runtime_config=runtime_config)

    import clr
    for dll_path in dll_paths:
        clr.AddReference(path + dll_path) # pylint: disable=no-member

    for library in LIBRARIES:
        library.load()

    _LOADED = True


def unload_dotnet():
    global _LOADED
    if not _LOADED:
        return

    for library in reversed(LIBRARIES):
        library.unload()

    import pythonnet
    pythonnet.unload()

    _LOADED = False
