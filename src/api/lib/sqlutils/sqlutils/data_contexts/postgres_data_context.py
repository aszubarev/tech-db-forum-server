import logging
from contextlib import contextmanager
from typing import Any, Dict, Tuple, List

import psycopg2
from psycopg2 import errorcodes
from psycopg2 import IntegrityError
from psycopg2 import InternalError
import psycopg2.extras
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, ISOLATION_LEVEL_READ_COMMITTED, \
    ISOLATION_LEVEL_READ_UNCOMMITTED
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.psycopg1 import connection

from sqlutils.data_contexts.data_context import DataContext
from sqlutils.errors.not_null_violation import NotNUllViolation
from sqlutils.errors.unique_violation_error import UniqueViolationError
from sqlutils.errors.no_data_found_error import NoDataFoundError
from sqlutils.errors.foreign_key_violation_error import ForeignKeyViolationError
from sqlutils.errors.restrict_violation_error import RestrictViolationError
import os


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
        self._poolConnection = ThreadedConnectionPool(minconn=1, maxconn=12, host=host, port=port,
                                                      database=database, user=user, password=password)
        self._pid = os.getpid()

    def execute(self, cmd: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        conn, cursor = self._create_connection()
        try:
            # logging.info(f"[PostgresDataContext.execute] run  with pid = {self._pid}")
            cursor.execute(cmd, params)
            data = cursor.fetchall()
        except IntegrityError as ex:
            if ex.pgcode == errorcodes.UNIQUE_VIOLATION:
                raise UniqueViolationError
            elif ex.pgcode == errorcodes.FOREIGN_KEY_VIOLATION:
                raise ForeignKeyViolationError
            elif ex.pgcode == errorcodes.RESTRICT_VIOLATION:
                raise RestrictViolationError
            elif ex.pgcode == errorcodes.NOT_NULL_VIOLATION:
                raise NotNUllViolation
            raise
        except InternalError as ex:
            if ex.pgcode == errorcodes.NO_DATA_FOUND:
                raise NoDataFoundError
            raise
        finally:
            # logging.info(f"[PostgresDataContext.execute] stop with pid = {self._pid}")
            conn.commit()
            cursor.close()
            self._put_connection(conn=conn)
        return data

    def add_many(self, table: str, insert_values: str, insert_args: str) -> None:
        """
        :param table: table name
        :param insert_values: (id, data, ...)
        :param insert_args: "(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        :return: data
        """

        conn, cursor = self._create_connection()
        try:
            # logging.info(f"[PostgresDataContext.add_many] run  with pid = {self._pid}")
            query = f"INSERT INTO {table} {insert_values} VALUES {insert_args};"
            cursor.execute(query)
        except IntegrityError as ex:
            if ex.pgcode == errorcodes.UNIQUE_VIOLATION:
                raise UniqueViolationError
            elif ex.pgcode == errorcodes.FOREIGN_KEY_VIOLATION:
                raise ForeignKeyViolationError
            elif ex.pgcode == errorcodes.RESTRICT_VIOLATION:
                raise RestrictViolationError
            elif ex.pgcode == errorcodes.NOT_NULL_VIOLATION:
                raise NotNUllViolation
            raise
        except InternalError as ex:
            if ex.pgcode == errorcodes.NO_DATA_FOUND:
                raise NoDataFoundError
            raise
        finally:
            # logging.info(f"[PostgresDataContext.add_many] stop with pid = {self._pid}")
            conn.commit()
            cursor.close()
            self._put_connection(conn=conn)

    def callproc(self, cmd, params):
        conn, cursor = self._create_connection()
        try:
            # logging.info(f"[PostgresDataContext.callproc] run  with pid = {self._pid}")
            cursor.callproc(cmd, params)
            data = cursor.fetchall()
        except IntegrityError as ex:
            # logging.error(f"[PostgresDataContext.callproc] error code = {ex.pgcode}")
            if ex.pgcode == errorcodes.UNIQUE_VIOLATION:
                raise UniqueViolationError
            elif ex.pgcode == errorcodes.FOREIGN_KEY_VIOLATION:
                raise ForeignKeyViolationError
            elif ex.pgcode == errorcodes.RESTRICT_VIOLATION:
                raise RestrictViolationError
            elif ex.pgcode == errorcodes.NOT_NULL_VIOLATION:
                raise NotNUllViolation
            raise
        except InternalError as ex:
            if ex.pgcode == errorcodes.NO_DATA_FOUND:
                raise NoDataFoundError
            raise
        finally:
            # logging.info(f"[PostgresDataContext.callproc] stop with pid = {self._pid}")
            conn.commit()
            cursor.close()
            self._put_connection(conn=conn)
        return data

    def _get_connection(self):
        return self._poolConnection.getconn()

    def _put_connection(self, conn):
        self._poolConnection.putconn(conn=conn)

    def _create_connection(self) -> Tuple[connection, RealDictCursor]:
        conn = self._get_connection()
        conn.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        return conn, cursor

    def get_by_id(self, collection: str, key: str = None, value: Any = None) -> Dict[str, Any]:
        return NotImplemented

    def get_all(self, collection: str) -> List[Dict[str, Any]]:
        return NotImplemented

    def add(self, collection: str, data: Dict[str, Any]) -> Any:
        return NotImplemented

    def delete(self, collection: str, key: str, uid: Any) -> None:
        return NotImplemented

    def update(self, collection: str, key: str, data: Dict[str, Any]) -> None:
        return NotImplemented
