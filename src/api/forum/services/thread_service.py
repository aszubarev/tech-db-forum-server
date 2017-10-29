from typing import Optional, List, Any, Dict

import dateutil.parser
from flask import request
from injector import inject, singleton

from forum.persistence.dto.vote_dto import VoteDTO
from sqlutils import Service, NoDataFoundError

from forum.cache import cache
from forum.converters.thread_converter import ThreadConverter
from forum.models.thread import Thread
from forum.persistence.dto.thread_dto import ThreadDTO
from forum.persistence.repositories.thread_repository import ThreadRepository
from forum.services.forum_service import ForumService


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

    def add(self, entity: ThreadDTO) -> Optional[Thread]:
        dto = self._repo.add(entity)
        self._forum_service.increment_threads(entity.forum_id)
        self._clear_cache()
        return self._convert(dto)

    def vote(self, entity: VoteDTO) -> Optional[int]:
        """
        Function returning number of vote for thread
        :param entity: VoteDTO
        :return votes: int 
        """
        votes = self.__repo.vote(entity)
        self._clear_cache()
        return votes

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

        return thread

    @cache.memoize(600)
    def get_by_id_setup(self, uid: int, load_forum: bool) -> Optional[Thread]:
        data = self._repo.get_by_id_setup(uid, load_forum)
        return self._convert(data)

    @cache.memoize(600)
    def get_by_slug_setup(self, slug: str, load_forum: bool) -> Optional[Thread]:
        data = self._repo.get_by_slug_setup(slug, load_forum)
        return self._convert(data)

    @cache.memoize(600)
    def get_by_slug_or_id_setup(self, slug_or_id: str, load_forum: bool = False) -> Optional[Thread]:
        try:
            cast_thread_id = int(slug_or_id)
            thread = self.get_by_id_setup(cast_thread_id, load_forum)

        except ValueError:
            thread_slug = slug_or_id
            thread = self.get_by_slug_setup(thread_slug, load_forum)

        return thread

    @cache.memoize(600)
    def get_number_threads_for_forum(self, forum_id: int) -> Optional[int]:
        data = self.__repo.get_number_threads_for_forum(forum_id)
        return data

    @cache.memoize(600)
    def get_count(self) -> int:
        return self.__repo.get_count()

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

    def clear(self) -> None:
        self.__repo.clear()
        self._clear_cache()

    @staticmethod
    def _clear_cache() -> None:
        # TODO don't remember update cache
        cache.delete_memoized(ThreadService.get_by_id)
        cache.delete_memoized(ThreadService.get_by_slug)
        cache.delete_memoized(ThreadService.get_by_slug_or_id)

        cache.delete_memoized(ThreadService.get_number_threads_for_forum)

        cache.delete_memoized(ThreadService.get_by_id_setup)
        cache.delete_memoized(ThreadService.get_by_slug_setup)
        cache.delete_memoized(ThreadService.get_by_slug_or_id_setup)

        cache.delete_memoized(ThreadService.get_count)
