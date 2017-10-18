import logging
from typing import Optional, List

import dateutil.parser
from flask import request
from injector import inject, singleton
from sqlutils import Service, NoDataFoundError

from tech_forum_api.cache import cache
from tech_forum_api.converters.post_converter import PostConverter
from tech_forum_api.models.post import Post
from tech_forum_api.persistence.dto.post_dto import PostDTO
from tech_forum_api.persistence.repositories.post_repository import PostRepository
from tech_forum_api.services.thread_service import ThreadService


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

    def get_by_id(self, uid: int) -> Optional[Post]:
        return super().get_by_id(uid)

    def get_posts_for_thread(self, thread_slug_or_id: str) -> List[Post]:

        try:
            thread_id = int(thread_slug_or_id)

        except ValueError:
            thread_slug = thread_slug_or_id
            thread = self._thread_service.get_by_slug(slug=thread_slug)
            if not thread:
                raise NoDataFoundError("Can't find thread by slug = {thread_slug_or_id}")
            thread_id = thread.uid

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

    @staticmethod
    def _clear_cache() -> None:
        # cache.delete_memoized(PostService.get_by_id)
        pass
        #TODO dont remember update cache
