from typing import Callable
import bpy

def col_prop(
    layout: bpy.types.UILayout,
    data: any,
    property: str,
    text=None):

    if text is None:
        text = data.bl_rna.properties[property].name

    layout.column(heading=text)\
        .prop(data, property, text="")


def prop_advanced(
        layout: bpy.types.UILayout,
        label: str,
        data1: any,
        property1: str,
        data2: any = None,
        property2: str | None = None,
        active=True):


    if isinstance(getattr(data1, property1), bool):
        col = layout.column(heading=label)
        col.active = active
        col.use_property_decorate = False
        col.use_property_split = True
        col.prop(data1, property1, text="")
    else:
        col = layout.column()
        col.active = active
        col.use_property_decorate = False
        col.use_property_split = True
        col.prop(data1, property1, text=label)



    # if not auto_scale:
    #     split = layout.split(factor=0.5)
    #     split.active = active

    #     row = split.row()
    #     row.alignment = 'LEFT'

    #     if data2 is not None and property2 is not None:
    #         row.prop(data2, property2, text="")

    #     row.label(text=label)
    #     split.prop(data1, property1, text="")


def local_prop_advanced(layout: bpy.types.UILayout, data1: any, data2: any = None):
    def prop_callback_callback(label: str, property1: str, property2: str | None = None, active=True):
        prop_advanced(layout, label, data1, property1, data2, property2, active)

    return prop_callback_callback


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
