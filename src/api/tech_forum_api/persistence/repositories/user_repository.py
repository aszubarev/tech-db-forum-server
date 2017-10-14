from typing import Optional, List

from injector import inject
from sqlutils import DataContext, Repository, create_one, create_many

from tech_forum_api.persistence.dto.user_dto import UserDTO


class UserRepository(Repository[UserDTO]):

    @inject
    def __init__(self, context: DataContext) -> None:
        self._context = context

    def get_by_id(self, uid: int) -> Optional[UserDTO]:
        data = self._context.callproc('get_user_by_id', [uid])
        return create_one(UserDTO, data)

    def get_by_nickname(self, nickname: str) -> Optional[UserDTO]:
        data = self._context.callproc('get_user_by_nickname', [nickname])
        return create_one(UserDTO, data)

    def get_by_nickname_or_email(self, nickname: str, email: str) -> List[UserDTO]:
        data = self._context.callproc('get_users_by_nickname_or_email', [nickname, email])
        return create_many(UserDTO, data)

    def get_all(self) -> List[UserDTO]:
        raise NotImplementedError

    def add(self, entity: UserDTO) -> Optional[UserDTO]:
        data = self._context.callproc('add_user', [entity.nickname, entity.email, entity.about, entity.fullname])
        return create_one(UserDTO, data)

    def update(self, entity: UserDTO) -> None:
        self._context.callproc('update_user_by_nickname', [entity.nickname, entity.email,
                                                           entity.about, entity.fullname])

    def delete(self, uid: int) -> None:
        raise NotImplementedError
