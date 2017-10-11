from abc import abstractmethod
from typing import Generic, TypeVar


T = TypeVar("T")
E = TypeVar("E")


class Converter(Generic[T, E]):

    @abstractmethod
    def convert(self, entity: E) -> T:
        pass
