from typing import Any, Dict, List, Optional

from .data_context import DataContext


class MongoDataContext(DataContext):

    def __init__(self, host: str, port: int, db: str, user: str, pwd: str) -> None:
        from pymongo import MongoClient
        self.__mongo_client = MongoClient

        credentials = ''
        if user and pwd:
            credentials = f'{user}:{pwd}@'
        self._conn_string = f'mongodb://{credentials}{host}:{port}/{db}'
        self._db = db

    @property
    def conn_string(self) -> str:
        return self._conn_string

    def execute(self, cmd: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def callproc(self, cmd: str, params: List[Any]) -> List[Dict[str, Any]]:

        raise NotImplementedError

    def add(self, collection: str, data: Dict[str, Any]) -> Any:
        with self.__mongo_client(self._conn_string) as client:
            db = client[self._db]
            return db[collection].insert_one(data)

    def update(self, collection: str, key: str, data: Dict[str, Any]) -> None:
        with self.__mongo_client(self._conn_string) as client:
            db = client[self._db]
            db[collection].replace_one({key or 'id': data[key or 'id']}, data, True)

    def delete(self, collection: str, key: str, uid: Any) -> None:
        with self.__mongo_client(self._conn_string) as client:
            db = client[self._db]
            db[collection].delete_one({key or 'id': uid})

    def get_by_id(self, collection: str, key: str = None, uid: Any = None) -> Optional[Dict[str, Any]]:
        with self.__mongo_client(self._conn_string) as client:
            db = client[self._db]
            data = db[collection].find_one({key or 'id': uid})
            return data

    def get_all(self, collection: str) -> List[Dict[str, Any]]:
        with self.__mongo_client(self._conn_string) as client:
            db = client[self._db]
            return db[collection].find({})
