from abc import abstractmethod
from typing import Any, Dict, Generic, TypeVar

# noinspection PyUnresolvedReferences
from sqlutils import Entity, Model, AbstractExpandSet

T = TypeVar("T", bound="Model")
E = TypeVar("E", bound="Entity")


class Serializer(Generic[T, E]):

    @abstractmethod
    def dump(self, model: T) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def load(self, data: Dict[str, Any]) -> E:
        raise NotImplementedError
