from abc import abstractmethod
from typing import Any, Dict, Generic, TypeVar, List

# noinspection PyUnresolvedReferences
from sqlutils import Entity, Model, AbstractExpandSet

T = TypeVar("T", bound="Model")
E = TypeVar("E", bound="Entity")


class Serializer(Generic[T, E]):

    @abstractmethod
    def dump(self, model: T) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def prepare_load_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def load(self, data: Dict[str, Any]) -> E:
        raise NotImplementedError
