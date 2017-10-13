from typing import Dict, Any, Optional
from apiutils import Serializer

from tech_forum_api.models.user import User
from tech_forum_api.persistence.dto.user_dto import UserDTO


class UserSerializer(Serializer):

    @staticmethod
    def dump(model: User) -> Optional[Dict[str, Any]]:

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

    @staticmethod
    def load(data: Dict[str, Any]) -> UserDTO:
        user_id = None if data['id'] is None or data['id'] == 'null' else int(data['id'])
        nickname = data['nickname']
        email = data['nickname']
        about = data['about']
        fullname = data['fullname']
        return UserDTO(user_id, nickname, email, about, fullname)
