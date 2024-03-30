from typing import Callable
import bpy


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
        if prop2 is not None and prop2Name is not None:
            row.prop(prop2, prop2Name, text="")
        row.label(text=label)
        split.prop(prop1, prop1Name, text="")

    else:
        row = layout.row()
        row.alignment = 'LEFT'
        if prop2 is not None and prop2Name is not None:
            row.prop(prop2, prop2Name, text="")
        row.label(text=label)
        row.alignment = 'EXPAND'
        row.prop(prop1, prop1Name, text="")


TOOL_PROPERTY = tuple[str, str, dict]


def draw_list(
        layout: bpy.types.UILayout,
        ui_list: bpy.types.UIList,
        context_menu: bpy.types.Menu | None,
        target_list,
        tools: list[TOOL_PROPERTY],
        per_op: Callable[[bpy.types.Operator, int], None] | None):

    row = layout.row()
    row.template_list(
        ui_list.bl_rna.identifier,
        "",
        target_list,
        "elements",
        target_list,
        "active_index")

    column = row.column()

    for i, tool in enumerate(tools):
        if tool is None:
            column.separator()
            continue

        operator = column.operator(
            tool[0],
            icon=tool[1],
            text="")

        for k, v in tool[2].items():
            setattr(operator, k, v)

        if per_op is not None:
            per_op(operator, i)

    if context_menu is not None:
        column.menu(
            context_menu.bl_rna.identifier,
            icon='DOWNARROW_HLT',
            text="")


def draw_error_box(layout: bpy.types.UILayout, error: str | None):
    if error is None:
        return False
    layout.box().label(text=error)
    return True
