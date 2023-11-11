import bpy
from bpy.props import IntProperty


class BaseList(bpy.types.PropertyGroup):

    active_index: IntProperty(
        name="Active texture index",
        description="Index of active item in the list",
        default=-1
    )

    def __iter__(self):
        return self.elements.__iter__()

    def __len__(self):
        return self.elements.__len__()

    def __getitem__(self, key: int | str):
        if isinstance(key, int):
            return self.elements[key]
        return super().__getitem__(key)

    @classmethod
    def _get_index_comparator(cls, value):
        raise NotImplementedError()

    def _on_created(self, value, **args):
        pass

    def _on_clear(self):
        pass

    def get_index(self, value):
        comparator = self._get_index_comparator(value)
        for i, item in enumerate(self):
            if comparator(item):
                return i

        return None

    def new(self, **args):
        result = self.elements.add()
        self._on_created(result, **args)
        self.active_index = len(self) - 1
        return result

    def remove(self, value):
        if isinstance(value, int):
            index = value
        else:
            index = self.get_index(value)

        if index is None or index >= len(self):
            return

        self.elements.remove(index)

        if self.active_index == index:
            self.active_index -= 1

        if len(self) == 0:
            self.active_index = -1
        elif self.active_index < 0:
            self.active_index = 0

    def move(self, old_index: int, new_index: int):
        self.elements.move(
            old_index,
            new_index)

        if self.active_index == old_index:
            self.active_index = new_index

    def clear(self):
        self._on_clear()
        self.elements.clear()
        self.active_index = -1
