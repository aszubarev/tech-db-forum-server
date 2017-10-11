from sqlutils.data_contexts.data_context_factory import DataContextFactory


class ConfigDataContextFactory(DataContextFactory):

    """
    :type _config_file: str
    """

    def __init__(self, config_file):
        """
        :type config_file: str
        """
        self._config_file = config_file

    def create_data_context(self):
        # TODO: read config file and return postgres data context
        return NotImplementedError
        # return PostgresDataContext()

