import logging
from typing import Optional, List

import dateutil.parser
from flask import request
from injector import inject, singleton
from sqlutils import Service, NoDataFoundError

from forum.cache import cache
from forum.converters.post_converter import PostConverter
from forum.models.post import Post
from forum.persistence.dto.post_dto import PostDTO
from forum.persistence.repositories.post_repository import PostRepository
from forum.services.thread_service import ThreadService


@singleton
class PostService(Service[Post, PostDTO, PostRepository]):

    @inject
    def __init__(self, repo: PostRepository, thread_service: ThreadService) -> None:
        super().__init__(repo)
        self._converter = PostConverter()
        self._thread_service = thread_service

    @property
    def __repo(self) -> PostRepository:
        return self._repo

    @cache.memoize(600)
    def get_by_id(self, uid: int) -> Optional[Post]:
        return super().get_by_id(uid)

    @cache.memoize(600)
    def get_number_posts_for_forum(self, forum_id: int) -> int:
        data = self.__repo.get_number_posts_for_forum(forum_id)
        return data

    @cache.memoize(600)
    def get_count(self) -> int:
        return self.__repo.get_count()

    # TODO refactor this shit
    def get_posts_for_thread(self, thread_id: int) -> List[Post]:

        desc = request.args.get('desc')
        limit = request.args.get('limit')
        since = request.args.get('since')
        sort = request.args.get('sort')

        entities = self.__repo.get_posts_for_thread(thread_id=thread_id, desc=desc, limit=limit, since=since, sort=sort)
        return self._convert_many(entities)

    def _convert(self, entity: PostDTO) -> Optional[Post]:
        if not entity:
            return None

        return self._converter.convert(entity)

    def clear(self) -> None:
        self.__repo.clear()
        self._clear_cache()

    @staticmethod
    def _clear_cache() -> None:
        # TODO don't remember update cache
        cache.delete_memoized(PostService.get_by_id)
        cache.delete_memoized(PostService.get_number_posts_for_forum)
        cache.delete_memoized(PostService.get_count)
