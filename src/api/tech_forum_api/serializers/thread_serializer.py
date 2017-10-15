import logging
from datetime import datetime
from typing import Dict, Any, Optional

import dateutil.parser
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
                'id': model.uid,
                'author': author.nickname,
                'forum': forum.slug,
                'message': model.message,
                'title': model.title

            })

            if model.created is not None:
                data.update({
                    'created': model.created.astimezone().isoformat()
                })

            if model.slug is not None:
                data.update({
                    'slug': model.slug
                })

        return data

    def prepare_load_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {}

    def load(self, data: Dict[str, Any]) -> ThreadDTO:

        logging.info(f"[ThreadSerializer.load] Try load entity")

        author = self._userService.get_by_nickname(data.get('author'))
        if not author:
            logging.error(f"[ThreadSerializer.load] Can't find author for thread by nickname = {data.get('author')}")
            raise NoDataFoundError(f"Can't find author for thread by nickname = {data.get('author')}")

        forum = self._forum_service.get_by_slug(data.get('forum'))
        if not forum:
            logging.error(f"[ThreadSerializer.load] Can't find author for thread by nickname = {data.get('forum')}")
            raise NoDataFoundError(f"Can't find forum for thread by nickname = {data.get('forum')}")

        thread_id = None if data.get('id') is None or data.get('id') == 'null' else data['id']
        slug = None if data.get('slug') is None or data.get('slug') == 'null' else data['slug']
        forum_id = forum.uid
        user_id = author.uid
        created = None if data.get('created') is None or data.get('created') == 'null' else dateutil.parser.parse(data['created'])
        message = None if data.get('message') is None or data.get('message') == 'null' else data['message']
        title = None if data.get('title') is None or data.get('title') == 'null' else data['title']

        logging.info(f"[ThreadSerializer.load] Complete load entity")

        return ThreadDTO(uid=thread_id, slug=slug, forum_id=forum_id, user_id=user_id,
                         created=created, message=message, title=title)
