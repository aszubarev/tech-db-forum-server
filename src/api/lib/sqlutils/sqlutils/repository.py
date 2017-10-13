from abc import abstractmethod
from typing import List, Any, Generic, TypeVar

from sqlutils.entity import Entity

T = TypeVar("T")


class Repository(Generic[T]):

    @abstractmethod
    def get_by_id(self, uid: Any) -> T:
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> List[T]:
        raise NotImplementedError

    @abstractmethod
    def add(self, entity: T) -> None:
        raise NotImplementedError

    @abstractmethod
    def update(self, entity: T) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, uid: Any) -> None:
        raise NotImplementedError
