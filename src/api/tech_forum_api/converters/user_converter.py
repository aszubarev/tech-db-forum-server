from sqlutils import Converter

from tech_forum_api.models.user import User
from tech_forum_api.persistence.dto.user_dto import UserDTO


class UserConverter(Converter[User, UserDTO]):

    def convert(self, entity: UserDTO) -> User:
        return User(uid=entity.uid).fill(
            nickname=entity.nickname,
            email=entity.email,
            about=entity.about,
            fullname=entity.fullname
        )
