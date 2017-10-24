import logging
from typing import Optional, List

from injector import inject, singleton
from sqlutils import Service, NoDataFoundError

from forum.cache import cache
from forum.converters.forum_converter import ForumConverter
from forum.models.forum import Forum
from forum.persistence.dto.forum_dto import ForumDTO
from forum.persistence.repositories.forum_repository import ForumRepository


@singleton
class ForumService(Service[Forum, ForumDTO, ForumRepository]):

    @inject
    def __init__(self, repo: ForumRepository) -> None:
        super().__init__(repo)
        self._converter = ForumConverter()

    @property
    def __repo(self) -> ForumRepository:
        return self._repo

    def increment_threads(self, uid: int):
        self.__repo.increment_threads(uid)
        self._clear_cache()

    def increment_posts(self, uid: int):
        self.__repo.increment_posts(uid)
        self._clear_cache()

    @cache.memoize(600)
    def get_by_id(self, uid: int) -> Optional[Forum]:
        return super().get_by_id(uid)

    @cache.memoize(600)
    def get_by_slug(self, slug: str) -> Optional[Forum]:
        dto = self.__repo.get_by_slug(slug)
        model = self._convert(dto)
        return model

    @cache.memoize(600)
    def get_count(self) -> int:
        return self.__repo.get_count()

    def _convert(self, entity: ForumDTO) -> Optional[Forum]:
        if not entity:
            return None

        return self._converter.convert(entity)

    def clear(self) -> None:
        self.__repo.clear()
        self._clear_cache()

    @staticmethod
    def _clear_cache() -> None:
        # TODO don't remember update cache
        cache.delete_memoized(ForumService.get_by_id)
        cache.delete_memoized(ForumService.get_by_slug)
        cache.delete_memoized(ForumService.get_count)

