from typing import Optional, List

from flask import request
from injector import inject, singleton

from sqlutils import Service

from tech_forum_api.cache import cache
from tech_forum_api.converters.user_converter import UserConverter
from tech_forum_api.models.user import User
from tech_forum_api.persistence.dto.user_dto import UserDTO
from tech_forum_api.persistence.repositories.user_repository import UserRepository


@singleton
class UserService(Service[User, UserDTO, UserRepository]):

    @inject
    def __init__(self, repo: UserRepository) -> None:
        super().__init__(repo)
        self._converter = UserConverter()

    @property
    def __repo(self) -> UserRepository:
        return self._repo

    @cache.memoize(600)
    def get_by_id(self, uid: int) -> Optional[User]:
        return super().get_by_id(uid)

    @cache.memoize(600)
    def get_by_nickname(self, nickname: str) -> Optional[User]:
        data = self.__repo.get_by_nickname(nickname)
        return self._convert(data)

    @cache.memoize(600)
    def get_by_nickname_or_email(self, nickname: str, email: str) -> List[User]:
        data = self.__repo.get_by_nickname_or_email(nickname, email)
        return self._convert_many(data)

    @cache.memoize(600)
    def get_count(self) -> int:
        return self.__repo.get_count()

    def get_for_forum(self, forum_id: int) -> List[User]:

        desc = request.args.get('desc')
        limit = request.args.get('limit')
        since = request.args.get('since')

        data = self.__repo.get_for_forum(forum_id, since=since, limit=limit, desc=desc)
        return self._convert_many(data)

    def _convert(self, entity: UserDTO) -> Optional[User]:
        if not entity:
            return None

        return self._converter.convert(entity)

    def clear(self) -> None:
        self.__repo.clear()
        self._clear_cache()

    @staticmethod
    def _clear_cache() -> None:
        # TODO don't remember update cache
        cache.delete_memoized(UserService.get_by_id)
        cache.delete_memoized(UserService.get_by_nickname)
        cache.delete_memoized(UserService.get_by_nickname_or_email)
        cache.delete_memoized(UserService.get_count)
