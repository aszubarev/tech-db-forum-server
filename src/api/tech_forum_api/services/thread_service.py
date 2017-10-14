import logging
from typing import Optional, List

from injector import inject, singleton
from sqlutils import Service, NoDataFoundError

from tech_forum_api.cache import cache
from tech_forum_api.converters.thread_converter import ThreadConverter
from tech_forum_api.models.thread import Thread
from tech_forum_api.persistence.dto.thread_dto import ThreadDTO
from tech_forum_api.persistence.repositories.thread_repository import ThreadRepository


@singleton
class ThreadService(Service[Thread, ThreadDTO, ThreadRepository]):

    @inject
    def __init__(self, repo: ThreadRepository) -> None:
        super().__init__(repo)
        self._converter = ThreadConverter()

    @property
    def __repo(self) -> ThreadRepository:
        return self._repo

    def get_by_id(self, uid: int) -> Optional[Thread]:
        return super().get_by_id(uid)

    def _convert(self, entity: ThreadDTO) -> Optional[Thread]:
        if not entity:
            return None

        return self._converter.convert(entity)

    @staticmethod
    def _clear_cache() -> None:
        # cache.delete_memoized(ThreadService.get_by_id)
        pass
        #TODO dont remember update cache
