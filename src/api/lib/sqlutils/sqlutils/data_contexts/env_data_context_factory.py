import os

from sqlutils.data_contexts.data_context_factory import DataContextFactory
from sqlutils.data_contexts.postgres_data_context import PostgresDataContext


class EnvDataContextFactory(DataContextFactory):

    def __init__(self):
        pass

    def create_data_context(self):
        # TODO: make decision about database type and load properly variables: add switches
        host = os.environ['DB_HOST']
        port = os.environ['DB_PORT']
        database = os.environ['DB_NAME']
        user = os.environ['DB_USER']
        password = os.environ['DB_PASS']

        return PostgresDataContext(host, port, database, user, password)
