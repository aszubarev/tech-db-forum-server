from typing import Optional, List, Dict, Any

from flask import request
from injector import inject, singleton

from forum.services.forum_service import ForumService
from sqlutils import Service

from forum.cache import cache
from forum.converters.post_converter import PostConverter
from forum.models.post import Post
from forum.persistence.dto.post_dto import PostDTO
from forum.persistence.repositories.post_repository import PostRepository


@singleton
class PostService(Service[Post, PostDTO, PostRepository]):

    @inject
    def __init__(self, repo: PostRepository, forum_service: ForumService) -> None:
        super().__init__(repo)
        self._converter = PostConverter()
        self._forum_service = forum_service

    @property
    def __repo(self) -> PostRepository:
        return self._repo

    def next_uid(self) -> int:
        return self.__repo.next_uid()

    def add_many(self, insert_values: str, insert_args: str) -> None:
        self.__repo.add_many(insert_values=insert_values, insert_args=insert_args)
        self._clear_cache()

    def update_soft(self, uid: int, message: str) -> Optional[Dict[str, Any]]:
        response = self.__repo.update_soft(uid=uid, message=message)
        self._clear_cache()
        return response

    @cache.memoize(600)
    def get_by_id(self, uid: int) -> Optional[Post]:
        return super().get_by_id(uid)

    @cache.memoize(600)
    def get_by_id_setup(self, uid: int, load_path: bool = False, load_thread: bool = False) -> Optional[Post]:
        data = self._repo.get_by_id_setup(uid, load_path, load_thread)
        return self._convert(data)

    @cache.memoize(600)
    def get_number_posts_for_forum(self, forum_id: int) -> int:
        data = self.__repo.get_number_posts_for_forum(forum_id)
        return data

    @cache.memoize(600)
    def get_count(self) -> int:
        return self.__repo.get_count()

    def get_posts_for_thread(self, thread_id: int) -> List[Dict[str, Any]]:
        desc = request.args.get('desc')
        limit = request.args.get('limit')
        since = request.args.get('since')
        sort = request.args.get('sort')

        return self.__repo.get_posts_for_thread(thread_id=thread_id, desc=desc, limit=limit, since=since, sort=sort)

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
        cache.delete_memoized(PostService.get_by_id_setup)
        cache.delete_memoized(PostService.get_count)
