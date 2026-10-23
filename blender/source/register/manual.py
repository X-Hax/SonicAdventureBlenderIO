import bpy
import inspect

TYPE_PAGE_MAP = {
}

OPS_PAGE_MAP = {
}

def _to_link(path: str, dir: str):
    return "/" + dir + ".html#" + path.replace(".", "-").replace("_", "-")

def _to_ui_link(path: str, dir: str):
    return _to_link(path, "user_interface/" + dir)


def get_mapping(classes):

    mapping = [
    ]

    for cls in classes:
        if issubclass(cls, bpy.types.Operator):
            path = "bpy.ops." + cls.bl_idname
            page_mapping = OPS_PAGE_MAP.get(cls.bl_idname, None)
        elif issubclass(cls, (bpy.types.PropertyGroup, bpy.types.AddonPreferences)):
            path = "bpy.types." + cls.__name__
            page_mapping = TYPE_PAGE_MAP.get(cls.__name__, None)
        else:
            continue

        if page_mapping is None:
            print(f"{path} = {page_mapping}")
            continue

        page = _to_ui_link(path, page_mapping)

        annotations = inspect.get_annotations(cls)
        for name in annotations.keys():
            mapping.append((
                (path + "." + name + "*").lower(),
                page + "-" + name.replace("_", "-")))

        mapping.append((
            (path + "*").lower(),
            page))

    return mapping
