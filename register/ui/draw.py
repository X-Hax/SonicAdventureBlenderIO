import bpy


class PropertiesPanel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_options = {"DEFAULT_CLOSED"}


def prop_advanced(
        layout: bpy.types.UILayout,
        label: str,
        prop1: any,
        prop1Name: str,
        prop2: any = None,
        prop2Name: str = None,
        autoScale=False):
    """Advanced Properties draw definition."""

    if not autoScale:
        split = layout.split(factor=0.5)
        row = split.row()
        row.alignment = 'LEFT'
        if prop2 is not None:
            row.prop(prop2, prop2Name, text="")
        row.label(text=label)
        split.prop(prop1, prop1Name, text="")

    else:
        row = layout.row()
        row.alignment = 'LEFT'
        if prop2 is not None:
            row.prop(prop2, prop2Name, text="")
        row.label(text=label)
        row.alignment = 'EXPAND'
        row.prop(prop1, prop1Name, text="")


def expand_icon(value):
    if value:
        return "TRIA_DOWN"
    else:
        return "TRIA_RIGHT"


def expand_menu(
        layout: bpy.types.UILayout,
        prop: any,
        name: str):

    opened = getattr(prop, name)

    layout.prop(
        prop,
        name,
        icon=expand_icon(opened),
        emboss=False
    )

    return getattr(prop, name)
