from .general import get_path
from ..exceptions import UserException

_LOADED = False


def load_library():
    global _LOADED
    if _LOADED:
        return True

    try:
        import pythonnet
    except ModuleNotFoundError:
        raise UserException((
            "Could not install python.net, please try running blender with"
            " admin rights"))

    path = get_path() + "\\DLL\\"
    dll_paths = [
        "SA3D.Modeling.Blender.dll",
        "SA3D.Archival.dll",
        "TextCopy.dll",
    ]

    runtime_config = f"{path}SA3D.Modeling.Blender.runtimeconfig.json"

    import pythonnet
    pythonnet.load("coreclr", runtime_config=runtime_config)

    import clr
    for dll_path in dll_paths:
        clr.AddReference(path + dll_path)

    _LOADED = True


def unload_library():
    global _LOADED
    if not _LOADED:
        return

    import pythonnet
    pythonnet.unload()

    _LOADED = False
