from typing import Optional, List, Any, Dict

from flask import request
from injector import inject, singleton

from sqlutils import Service

from forum.cache import cache
from forum.converters.user_converter import UserConverter
from forum.models.user import User
from forum.persistence.dto.user_dto import UserDTO
from forum.persistence.repositories.user_repository import UserRepository


@singleton
class UserService(Service[User, UserDTO, UserRepository]):

    @inject
    def __init__(self, repo: UserRepository) -> None:
        super().__init__(repo)
        self._converter = UserConverter()

    def add_soft(self, body: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        body.update({
            'nickname': kwargs['nickname']
        })
        data = self.__repo.add(body)
        self._clear_cache()
        return data

    def update_soft(self, body: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        body.update({
            'nickname': kwargs['nickname']
        })
        data = self.__repo.update(body)
        self._clear_cache()
        return data

    @property
    def __repo(self) -> UserRepository:
        return self._repo

    def get_by_id(self, uid: int) -> Optional[Dict[str, Any]]:
        return self.__repo.get_by_id(uid)

    @cache.memoize(600)
    def get_by_nickname(self, nickname: str) -> Optional[Dict[str, Any]]:
        return self.__repo.get_by_nickname(nickname)

    @cache.memoize(600)
    def get_by_nickname_setup(self, nickname: str, load_nickname: bool = False):
        data = self.__repo.get_by_nickname_setup(nickname, load_nickname)
        return self._convert(data)

    @cache.memoize(600)
    def get_by_nickname_or_email(self, nickname: str, email: str) -> List[Dict[str, Any]]:
        return self.__repo.get_by_nickname_or_email(nickname=nickname, email=email)

    @cache.memoize(600)
    def get_count(self) -> int:
        return self.__repo.get_count()

    def get_for_forum(self, forum_id: int, args: Dict[str, Any]) -> List[Dict[str, Any]]:

        desc = args.get('desc')
        limit = args.get('limit')
        since = args.get('since')

        return self.__repo.get_for_forum(forum_id=forum_id, since=since, limit=limit, desc=desc)

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
        cache.delete_memoized(UserService.get_by_nickname)
        cache.delete_memoized(UserService.get_by_nickname_setup)
        cache.delete_memoized(UserService.get_by_nickname_or_email)
        cache.delete_memoized(UserService.get_count)
