from bpy.props import EnumProperty

class ListAdd:

    def list_execute(self, context, target_list):
        target_list.new()


class ListRemove:

    def list_execute(self, context, target_list):
        target_list.remove(target_list.active_index)


class ListMove:

    direction: EnumProperty(
        name="Direction",
        items=(
            ('UP', "up", "up"),
            ('DOWN', "down", "down"),
        )
    )

    def list_execute(self, context, target_list):
        old_index = target_list.active_index

        if old_index == -1:
            return

        new_index = (
            target_list.active_index
            + (-1 if self.direction == 'UP'
                else 1)
        )

        if new_index < 0 or new_index >= len(target_list):
            return

        target_list.move(
            old_index,
            new_index)


class ListClear:
    def list_execute(self, context, target_list):
        target_list.clear()