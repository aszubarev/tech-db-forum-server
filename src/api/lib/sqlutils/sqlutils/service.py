from abc import abstractmethod, abstractstaticmethod
from typing import List, Generic, TypeVar, Any
from uuid import uuid4

from .abstract_expand_set import AbstractExpandSet

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

    def get_by_id(self, uid: Any, expand: AbstractExpandSet) -> T:
        dto = self._repo.get_by_id(uid)
        return self._convert(dto, expand)

    def get_all(self, expand: AbstractExpandSet) -> List[T]:
        data = self._repo.get_all()
        return self._convert_many(data, expand)

    def _convert_many(self, data: List[E], expand: AbstractExpandSet) -> List[T]:
        models = []
        for entity in data:
            models.append(self._convert(entity, expand))
        return models

    def add(self, entity: E) -> Any:
        new_entity = entity.copy()
        if not self._need_save_id or new_entity.uid is None:
            new_entity._uid = uuid4()

        self._repo.add(new_entity)
        self._clear_cache()
        return new_entity.uid

    def update(self, entity: E) -> None:
        self._repo.update(entity)
        self._clear_cache()

    def delete(self, uid: Any) -> None:
        self._repo.delete(uid)
        self._clear_cache()

    @abstractmethod
    def _convert(self, entity: E, expand: AbstractExpandSet) -> T:
        raise NotImplementedError

    @staticmethod
    @abstractstaticmethod
    def _clear_cache():
        raise NotImplementedError
