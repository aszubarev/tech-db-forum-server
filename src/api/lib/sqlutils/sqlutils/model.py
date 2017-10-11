from typing import Any


class Model(object):

    def __init__(self, uid: Any) -> None:
        self._uid = uid
        self.__is_loaded = False

    @property
    def uid(self) -> Any:
        return self._uid

    @property
    def is_loaded(self) -> bool:
        return self.__is_loaded

    def _filled(self) -> None:
        self.__is_loaded = True
