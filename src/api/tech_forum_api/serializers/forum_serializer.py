from typing import Dict, Any, Optional

from injector import inject, singleton
import logging

from apiutils import Serializer

from tech_forum_api.models.forum import Forum
from tech_forum_api.persistence.dto.forum_dto import ForumDTO
from tech_forum_api.services.user_service import UserService
from sqlutils import NoDataFoundError


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

        user = self._userService.get_by_nickname(data.get('user'))
        if not user:
            raise NoDataFoundError(f"Can't find user by nickname = {data.get('user')}")

        forum_id = None if data.get('id') is None or data.get('id') == 'null' else int(data['id'])
        slug = None if data.get('slug') is None or data.get('slug') == 'null' else data['slug']
        user_id = user.uid
        title = None if data.get('title') is None or data.get('title') == 'null' else data['title']

        return ForumDTO(forum_id, slug, user_id, title)
