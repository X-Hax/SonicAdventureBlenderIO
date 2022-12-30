from ..utils import get_path

_LOADED = False


def load_library():
    global _LOADED
    if _LOADED:
        return

    path = get_path()
    dll_path = f"{path}\\DLL\\SAModel.Blender.dll"
    runtime_config = f"{path}\\DLL\\SAModel.Blender.runtimeconfig.json"

    import pythonnet
    pythonnet.load("coreclr", runtime_config=runtime_config)

    import clr
    clr.AddReference(dll_path)

    _LOADED = True


def unload_library():
    global _LOADED
    if not _LOADED:
        return

    import pythonnet
    pythonnet.unload()

    _LOADED = False
