from typing import Optional, List

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

    def get_by_id(self, uid: int) -> Optional[User]:
        return super().get_by_id(uid)

    def get_by_nickname_or_email(self, nickname: str, email: str) -> List[User]:
        data = self.__repo.get_by_nickname_or_email(nickname, email)
        return self._convert_many(data)

    def _convert(self, entity: UserDTO) -> Optional[User]:
        if not entity:
            return None

        return self._converter.convert(entity)

    @staticmethod
    def _clear_cache() -> None:
        # cache.delete_memoized(UserService.get_by_id)
        pass
        #TODO dont remember update cache
