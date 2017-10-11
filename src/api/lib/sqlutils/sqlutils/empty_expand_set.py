from .abstract_expand_set import AbstractExpandSet

from .expand_item import ExpandItem


class EmptyExpandSet(AbstractExpandSet):

    def append(self, item: ExpandItem) -> None:
        raise NotImplementedError

    def contains(self, item: ExpandItem) -> bool:
        return False

    def extract(self, parent: ExpandItem) -> "AbstractExpandSet":
        return EmptyExpandSet()
