from typing import Any, Dict, Tuple, List

import psycopg2
from psycopg2 import errorcodes
from psycopg2 import IntegrityError
from psycopg2 import InternalError
import psycopg2.extras
from psycopg2.extras import DictCursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.psycopg1 import connection

from sqlutils.data_contexts.data_context import DataContext
from sqlutils.errors.unique_violation_error import UniqueViolationError
from sqlutils.errors.no_data_found_error import NoDataFoundError
from sqlutils.errors.foreign_key_violation_error import ForeignKeyViolationError
from sqlutils.errors.restrict_violation_error import RestrictViolationError


class PostgresDataContext(DataContext):

    @property
    def conn_string(self) -> str:
        return f'{self._user}:{self._password}@{self._host}:{self._port}/{self._database}'

    def __init__(self, host: str, port: int, database: str, user: str, password: str) -> None:
        self._host = host
        self._port = port
        self._database = database
        self._user = user
        self._password = password

        psycopg2.extras.register_uuid()

    def execute(self, cmd: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        conn, cursor = self._create_connection()
        try:
            cursor.execute(cmd, params)
            data = cursor.fetchall()
        except IntegrityError as ex:
            if ex.pgcode == errorcodes.UNIQUE_VIOLATION:
                raise UniqueViolationError
            elif ex.pgcode == errorcodes.FOREIGN_KEY_VIOLATION:
                raise ForeignKeyViolationError
            elif ex.pgcode == errorcodes.RESTRICT_VIOLATION:
                raise RestrictViolationError
            raise
        except InternalError as ex:
            if ex.pgcode == errorcodes.NO_DATA_FOUND:
                raise NoDataFoundError
            raise
        finally:
            cursor.close()
            conn.close()
        return data

    def callproc(self, cmd, params):
        conn, cursor = self._create_connection()
        try:
            cursor.callproc(cmd, params)
            data = cursor.fetchall()
        except IntegrityError as ex:
            if ex.pgcode == errorcodes.UNIQUE_VIOLATION:
                raise UniqueViolationError
            elif ex.pgcode == errorcodes.FOREIGN_KEY_VIOLATION:
                raise ForeignKeyViolationError
            elif ex.pgcode == errorcodes.RESTRICT_VIOLATION:
                raise RestrictViolationError
            raise
        except InternalError as ex:
            if ex.pgcode == errorcodes.NO_DATA_FOUND:
                raise NoDataFoundError
            raise
        finally:
            cursor.close()
            conn.close()
        return data

    def get_by_id(self, collection: str, key: str = None, value: Any = None) -> Dict[str, Any]:
        query = f'SELECT * FROM {collection}'
        if not key:
            query += f' WHERE {key}=%(key)s'
        data = self.execute(query, {key: value})
        if len(data) == 0:
            raise NoDataFoundError
        return data[0]

    def get_all(self, collection: str) -> List[Dict[str, Any]]:
        return self.execute(f'SELECT * FROM {collection}', {})

    def add(self, collection: str, data: Dict[str, Any]) -> Any:
        columns = ', '.join(data.keys())
        values = ', '.join(f'%({k})s' for k in data.keys())
        query = f'INSERT INTO {collection} ({columns}) VALUES ({values})'
        self.execute(query, data)

    def delete(self, collection: str, key: str, uid: Any) -> None:
        query = f'DELETE FROM {collection} WHERE {key}=$(key)s'
        self.execute(query, {key: uid})

    def update(self, collection: str, key: str, data: Dict[str, Any]) -> None:
        update = ', '.join(f'{k}=$({k})s' for k in data.keys() if k != key)
        query = f'UPDATE {collection} SET {update} WHERE {key}=$(key)s'
        self.execute(query, data)

    def _create_connection(self) -> Tuple[connection, DictCursor]:
        conn = psycopg2.connect(host=self._host, port=self._port, database=self._database,
                                user=self._user, password=self._password)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor(cursor_factory=DictCursor)
        return conn, cursor
