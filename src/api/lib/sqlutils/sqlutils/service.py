from abc import abstractmethod, abstractstaticmethod
from typing import List, Generic, TypeVar, Any

# noinspection PyUnresolvedReferences
from .entity import Entity

# noinspection PyUnresolvedReferences
from .repository import Repository

T = TypeVar("T")
E = TypeVar("E", bound="Entity")
R = TypeVar("R", bound="Repository[Any]")


class Service(Generic[T, E, R]):

    def __init__(self, repo: R) -> None:
        self._repo = repo
        self._need_save_id = False

    def get_by_id(self, uid: Any) -> T:
        dto = self._repo.get_by_id(uid)
        return self._convert(dto)

    def get_all(self) -> List[T]:
        data = self._repo.get_all()
        return self._convert_many(data)

    def _convert_many(self, data: List[E]) -> List[T]:
        models = []
        for entity in data:
            models.append(self._convert(entity))
        return models

    def add(self, entity: E) -> T:
        dto = self._repo.add(entity)
        self._clear_cache()
        return self._convert(dto)

    def add_many(self, entities: List[E]) -> List[T]:
        data = self._repo.add_many(entities)
        self._clear_cache()
        return self._convert_many(data)

    def update(self, entity: E) -> T:
        dto = self._repo.update(entity)
        self._clear_cache()
        return self._convert(dto)

    def delete(self, uid: Any) -> None:
        self._repo.delete(uid)
        self._clear_cache()

    @abstractmethod
    def _convert(self, entity: E) -> T:
        raise NotImplementedError

    @staticmethod
    @abstractstaticmethod
    def _clear_cache():
        raise NotImplementedError
