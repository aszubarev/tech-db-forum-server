from typing import Dict, Any, Optional

from injector import inject, singleton

from apiutils import Serializer

from tech_forum_api.models.thread import Thread
from tech_forum_api.persistence.dto.thread_dto import ThreadDTO
from tech_forum_api.services.forum_service import ForumService
from tech_forum_api.services.user_service import UserService
from sqlutils import NoDataFoundError


@singleton
class ThreadSerializer(Serializer):

    @inject
    def __init__(self, user_service: UserService, forum_service: ForumService):
        self._userService = user_service
        self._forum_service = forum_service

    def dump(self, model: Thread) -> Optional[Dict[str, Any]]:

        if not model:
            return None

        data = {}
        author = self._userService.get_by_id(model.author.uid)
        forum = self._forum_service.get_by_id(model.forum.uid)

        if model.is_loaded:
            data.update({
                'author': author.nickname,
                'created': model.created,
                'forum': forum.slug,
                'message': model.message,
                'title': model.title

            })

        return data

    def load(self, data: Dict[str, Any]) -> ThreadDTO:

        author = self._userService.get_by_nickname(data.get('user'))
        if not author:
            raise NoDataFoundError(f"Can't find author for thread by nickname = {data.get('user')}")

        forum = self._forum_service.get_by_slug(data.get('forum'))
        if not forum:
            raise NoDataFoundError(f"Can't find forum for thread by nickname = {data.get('forum')}")

        slug = None if data.get('slug') is None or data.get('slug') == 'null' else data['slug']
        forum_id = forum.uid
        user_id = author.uid
        created = None if data.get('created') is None or data.get('created') == 'null' else data['created']
        message = None if data.get('message') is None or data.get('message') == 'null' else data['message']
        title = None if data.get('title') is None or data.get('title') == 'null' else data['title']

        return ThreadDTO(uid=forum_id, slug=slug, forum_id=forum_id,
                         user_id=user_id, created=created, message=message, title=title)
