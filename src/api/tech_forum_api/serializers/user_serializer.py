from typing import Dict, Any, Optional

from injector import inject, singleton

from apiutils import Serializer

from tech_forum_api.models.user import User
from tech_forum_api.persistence.dto.user_dto import UserDTO


@singleton
class UserSerializer(Serializer):

    @inject
    def __init__(self):
        pass

    def dump(self, model: User) -> Optional[Dict[str, Any]]:

        if not model:
            return None

        data = {}

        if model.is_loaded:
            data.update({
                'nickname': model.nickname,
                'email': model.email,
                'about': model.about,
                'fullname': model.fullname,
            })

        return data

    def load(self, data: Dict[str, Any]) -> UserDTO:
        user_id = None if data.get('id') is None or data.get('id') == 'null' else int(data['id'])
        nickname = data['nickname']
        email = data['email']
        about = data['about']
        fullname = data['fullname']
        return UserDTO(user_id, nickname, email, about, fullname)
