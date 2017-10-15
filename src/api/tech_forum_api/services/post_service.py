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


@singleton
class PostService(Service[Post, PostDTO, PostRepository]):

    @inject
    def __init__(self, repo: PostRepository) -> None:
        super().__init__(repo)
        self._converter = PostConverter()

    @property
    def __repo(self) -> PostRepository:
        return self._repo

    def get_by_id(self, uid: int) -> Optional[Post]:
        return super().get_by_id(uid)

    def _convert(self, entity: PostDTO) -> Optional[Post]:
        if not entity:
            return None

        return self._converter.convert(entity)

    @staticmethod
    def _clear_cache() -> None:
        # cache.delete_memoized(PostService.get_by_id)
        pass
        #TODO dont remember update cache
