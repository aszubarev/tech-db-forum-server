from abc import ABCMeta, abstractmethod

from .expand_item import ExpandItem


class AbstractExpandSet(metaclass=ABCMeta):

    @abstractmethod
    def append(self, item: ExpandItem) -> None:
        pass

    @abstractmethod
    def contains(self, item: ExpandItem) -> bool:
        pass

    @abstractmethod
    def extract(self, parent: ExpandItem) -> "AbstractExpandSet":
        pass
