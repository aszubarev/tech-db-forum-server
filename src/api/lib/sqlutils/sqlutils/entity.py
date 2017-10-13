from abc import abstractmethod
from typing import Any, Dict, Type, List, TypeVar

import copy

T = TypeVar('T', bound="Entity")


def create_one(cls: Type[T], data: List[Dict[str, Any]]) -> T:
    if data is None or len(data) == 0:
        return None
    return cls.create(data[0])


def create_many(cls: Type[T], data: List[Dict[str, Any]]) -> List[T]:
    entities = []
    for row in data:
        entities.append(cls.create(row))
    return entities


class Entity(object):

    def __init__(self, uid: Any) -> None:
        self._uid = uid

    @property
    @abstractmethod
    def _key_field(self) -> str:
        raise NotImplementedError

    @property
    def uid(self) -> Any:
        return self._uid

    def fill(self, values: Dict[str, Any]) -> None:
        for key, value in values.items():
            if key == self._key_field:
                self._uid = value
            else:
                setattr(self, '_{0}'.format(key), value)

    @classmethod
    def create(cls: Type[T], values: Dict[str, Any]) -> T:
        entity = cls() # type: ignore
        entity.fill(values)
        return entity

    def copy(self: T) -> T:
        entity = copy.deepcopy(self)
        return entity

    def set_new_id(self, uid: Any) -> None:
        if self.uid:
            raise AttributeError("Id already set")
        self._uid = uid
