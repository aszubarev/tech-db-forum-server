import logging
from typing import Optional, List

from injector import inject, singleton
from sqlutils import Service, NoDataFoundError

from tech_forum_api.cache import cache
from tech_forum_api.converters.forum_converter import ForumConverter
from tech_forum_api.models.forum import Forum
from tech_forum_api.persistence.dto.forum_dto import ForumDTO
from tech_forum_api.persistence.repositories.forum_repository import ForumRepository


@singleton
class ForumService(Service[Forum, ForumDTO, ForumRepository]):

    @inject
    def __init__(self, repo: ForumRepository) -> None:
        super().__init__(repo)
        self._converter = ForumConverter()

    @property
    def __repo(self) -> ForumRepository:
        return self._repo

    @cache.memoize(600)
    def get_by_id(self, uid: int) -> Optional[Forum]:
        return super().get_by_id(uid)

    @cache.memoize(600)
    def get_by_slug(self, slug: str) -> Optional[Forum]:
        dto = self.__repo.get_by_slug(slug)
        model = self._convert(dto)
        if not model:
            raise NoDataFoundError(f"Can't find forum by slug = {slug}")

        return model

    def _convert(self, entity: ForumDTO) -> Optional[Forum]:
        if not entity:
            return None

        return self._converter.convert(entity)

    @staticmethod
    def _clear_cache() -> None:
        # TODO don't remember update cache
        cache.delete_memoized(ForumService.get_by_id)
        cache.delete_memoized(ForumService.get_by_slug)

