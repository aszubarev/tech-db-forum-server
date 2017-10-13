from abc import abstractmethod
from typing import Any, Dict, Generic, TypeVar

# noinspection PyUnresolvedReferences
from sqlutils import Entity, Model, AbstractExpandSet

T = TypeVar("T", bound="Model")
E = TypeVar("E", bound="Entity")


class Serializer(Generic[T, E]):

    @staticmethod
    @abstractmethod
    def dump(model: T) -> Dict[str, Any]:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def load(data: Dict[str, Any]) -> E:
        raise NotImplementedError
