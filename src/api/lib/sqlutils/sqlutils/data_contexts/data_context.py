from abc import ABCMeta
from abc import abstractmethod
from typing import Dict, Any, List


class DataContext(metaclass=ABCMeta):

    @property
    @abstractmethod
    def conn_string(self) -> str:
        return NotImplemented

    @abstractmethod
    def execute(self, cmd: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        return NotImplemented

    @abstractmethod
    def callproc(self, cmd: str, params: List[Any]) -> List[Dict[str, Any]]:
        return NotImplemented

    @abstractmethod
    def get_by_id(self, collection: str, key: str = None, uid: Any = None) -> Dict[str, Any]:
        return NotImplemented

    @abstractmethod
    def get_all(self, collection: str) -> List[Dict[str, Any]]:
        return NotImplemented

    @abstractmethod
    def add(self, collection: str, data: Dict[str, Any]) -> Any:
        return NotImplemented

    @abstractmethod
    def update(self, collection: str, key: str, data: Dict[str, Any]) -> None:
        return NotImplemented

    @abstractmethod
    def delete(self, collection: str, key: str, uid: Any) -> None:
        return NotImplemented

