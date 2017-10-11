from typing import Set, List

from .empty_expand_set import EmptyExpandSet
from .abstract_expand_set import AbstractExpandSet
from .expand_item import ExpandItem


class ExpandSet(AbstractExpandSet):

    def __init__(self, items: List[ExpandItem] = None) -> None:
        self._items: Set[str] = set()
        if items:
            for item in items:
                self.append(item)

    def append(self, item: ExpandItem) -> None:
        self._items.add(str(item))

    def contains(self, item: ExpandItem) -> bool:
        return str(item) in self._items

    @staticmethod
    def load(expand: str) -> "AbstractExpandSet":
        if not expand:
            return EmptyExpandSet()

        expand_set = ExpandSet()

        items = expand.split(',')
        for item in items:
            expand_item = ExpandItem.load(item)
            expand_set.append(expand_item)

        return expand_set

    def extract(self, parent: ExpandItem) -> "AbstractExpandSet":
        result = ExpandSet()

        if parent.name not in self._items or parent.child:
            return result

        for item in self._items:
            item_repr = str(item)
            if item_repr.startswith(f'{parent.name}.'):
                item = item_repr[len(parent.name)+1:]
                result.append(ExpandItem.load(item))

        return result

    def __str__(self) -> str:
        return ' '.join(sorted(self._items))
