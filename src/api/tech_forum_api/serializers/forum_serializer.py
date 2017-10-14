from typing import Dict, Any, Optional

from injector import inject, singleton
import logging

from apiutils import Serializer

from tech_forum_api.models.forum import Forum
from tech_forum_api.persistence.dto.forum_dto import ForumDTO
from tech_forum_api.services.user_service import UserService


@singleton
class ForumSerializer(Serializer):

    @inject
    def __init__(self, user_service: UserService):
        self._userService = user_service

    def dump(self, model: Forum) -> Optional[Dict[str, Any]]:

        if not model:
            return None

        data = {}
        user = self._userService.get_by_id(model.user.uid)

        if model.is_loaded:
            data.update({
                'slug': model.slug,
                'title': model.title,
                'user': user.nickname
            })

        return data

    def load(self, data: Dict[str, Any]) -> ForumDTO:
        forum_id = None if data.get('id') is None or data.get('id') == 'null' else int(data['id'])
        slug = data['slug']
        user_id = self._userService.get_by_nickname(data['user']).uid
        title = data['title']
        return ForumDTO(forum_id, slug, user_id, title)
