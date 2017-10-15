import logging
from typing import Optional, List

from injector import inject, singleton
from sqlutils import Service, NoDataFoundError

from tech_forum_api.cache import cache
from tech_forum_api.converters.thread_converter import ThreadConverter
from tech_forum_api.models.thread import Thread
from tech_forum_api.persistence.dto.thread_dto import ThreadDTO
from tech_forum_api.persistence.repositories.thread_repository import ThreadRepository
from tech_forum_api.services.forum_service import ForumService


@singleton
class ThreadService(Service[Thread, ThreadDTO, ThreadRepository]):

    @inject
    def __init__(self, repo: ThreadRepository, forum_service: ForumService) -> None:
        super().__init__(repo)
        self._converter = ThreadConverter()
        self._forum_service = forum_service

    @property
    def __repo(self) -> ThreadRepository:
        return self._repo

    def get_by_id(self, uid: int) -> Optional[Thread]:
        return super().get_by_id(uid)

    def get_for_forum(self, slug: str) -> List[Thread]:
        forum = self._forum_service.get_by_slug(slug)
        if forum is None:
            raise NoDataFoundError(f"Can't find forum by slug = {slug}")

        logging.info(f"[ThreadService.get_by_forum_slug] forum.uid = {forum.uid}")
        data = self._repo.get_for_forum(forum.uid)
        logging.info(f"[ThreadService.get_by_forum_slug] data = {data}")
        return self._convert_many(data)

    def _convert(self, entity: ThreadDTO) -> Optional[Thread]:
        if not entity:
            return None

        return self._converter.convert(entity)

    @staticmethod
    def _clear_cache() -> None:
        # cache.delete_memoized(ThreadService.get_by_id)
        pass
        #TODO dont remember update cache
