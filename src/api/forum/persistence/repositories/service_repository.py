from injector import inject, singleton


@singleton
class SrvRepository(object):

    @inject
    def __init__(self) -> None:
        pass
