import logging
from typing import Optional, List, Any, Dict

import dateutil.parser
from flask import request
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

    @cache.memoize(600)
    def get_by_id(self, uid: int) -> Optional[Thread]:
        return super().get_by_id(uid)

    @cache.memoize(600)
    def get_by_slug(self, slug: str) -> Optional[Thread]:
        data = self._repo.get_by_slug(slug)
        return self._convert(data)

    @cache.memoize(600)
    def get_by_slug_or_id(self, slug_or_id: str) -> Optional[Thread]:

        try:
            cast_thread_id = int(slug_or_id)
            thread = self.get_by_id(cast_thread_id)

        except ValueError:
            thread_slug = slug_or_id
            thread = self.get_by_slug(thread_slug)

        if not thread:
            raise NoDataFoundError(f"Can't find thread by thread_slug_or_id = {slug_or_id}")

        return thread

    def update_by_uid(self, entity: ThreadDTO) -> Optional[Thread]:
        data = self.__repo.update_by_uid(entity)
        self._clear_cache()
        return self._convert(data)

    def update_by_slug(self, entity: ThreadDTO) -> Optional[Thread]:
        data = self.__repo.update_by_slug(entity)
        self._clear_cache()
        return self._convert(data)

    def get_for_forum(self, slug: str) -> List[Thread]:
        forum = self._forum_service.get_by_slug(slug)
        if forum is None:
            raise NoDataFoundError(f"Can't find forum by slug = {slug}")

        desc = request.args.get('desc')
        limit = request.args.get('limit')
        since = request.args.get('since')

        if since is not None:
            since = dateutil.parser.parse(since)

        data = self._repo.get_for_forum(forum.uid, desc=desc, limit=limit, since=since)
        return self._convert_many(data)

    def _convert(self, entity: ThreadDTO) -> Optional[Thread]:
        if not entity:
            return None

        return self._converter.convert(entity)

    @staticmethod
    def _clear_cache() -> None:
        # TODO don't remember update cache
        cache.delete_memoized(ThreadService.get_by_id)
        cache.delete_memoized(ThreadService.get_by_slug)
        cache.delete_memoized(ThreadService.get_by_slug_or_id)
