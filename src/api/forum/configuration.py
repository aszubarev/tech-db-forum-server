from injector import Module, singleton, provider

from sqlutils import DataContext, EnvDataContextFactory


class Configuration(Module):
    @singleton
    @provider
    def provide_context(self) -> DataContext:
        return EnvDataContextFactory().create_data_context()
