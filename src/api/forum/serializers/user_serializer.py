import logging
from typing import Dict, Any, Optional

from injector import inject, singleton

from apiutils import Serializer

from forum.models.user import User
from forum.persistence.dto.user_dto import UserDTO


@singleton
class UserSerializer(Serializer):

    @inject
    def __init__(self):
        pass

    def dump(self, model: User, **kwargs) -> Optional[Dict[str, Any]]:

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

    def prepare_load_data(self, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError

    def load(self, data: Dict[str, Any]) -> UserDTO:
        user_id = None if data.get('id') is None or data.get('id') == 'null' else int(data['id'])
        nickname = None if data.get('nickname') is None or data.get('nickname') == 'null' else data['nickname']
        email = None if data.get('email') is None or data.get('email') == 'null' else data['email']
        about = None if data.get('about') is None or data.get('about') == 'null'else data['about']
        fullname = None if data.get('fullname') is None or data.get('fullname') == 'null' else data['fullname']
        return UserDTO(user_id, nickname, email, about, fullname)
