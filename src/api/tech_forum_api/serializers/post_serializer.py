import logging
from datetime import datetime
from typing import Dict, Any, Optional

import dateutil.parser
from injector import inject, singleton

from apiutils import Serializer

from tech_forum_api.models.post import Post
from tech_forum_api.persistence.dto.post_dto import PostDTO
from tech_forum_api.services.forum_service import ForumService
from tech_forum_api.services.post_service import PostService
from tech_forum_api.services.thread_service import ThreadService
from tech_forum_api.services.user_service import UserService
from sqlutils import NoDataFoundError


@singleton
class PostSerializer(Serializer):

    @inject
    def __init__(self, post_service: PostService, thread_service: ThreadService,
                 user_service: UserService, forum_service: ForumService) -> None:
        self._post_service = post_service
        self._userService = user_service
        self._forum_service = forum_service
        self._thread_service = thread_service

    def dump(self, model: Post) -> Optional[Dict[str, Any]]:

        if not model:
            return None

        data = {}
        author = self._userService.get_by_id(model.author.uid)
        forum = self._forum_service.get_by_id(model.forum.uid)

        if model.is_loaded:
            data.update({
                'author': author.nickname,
                'forum': forum.slug,
                'thread': model.thread.uid,
                'message': model.message,
                'isEdited': model.is_edited

            })

            if model.created is not None:
                data.update({
                    'created': model.created.astimezone().isoformat()
                })

        return data

    def prepare_load_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        logging.info(f"[PostSerializer.prepare_load_data] Try load entity")

        thread_slug_or_id = data.get('thread')

        if thread_slug_or_id is None:
            logging.error(f"[PostSerializer.load] Bad request")
            raise NoDataFoundError(f"Bad request")

        try:
            cast_thread_id = int(thread_slug_or_id)
            thread = self._thread_service.get_by_id(cast_thread_id)

        except ValueError:
            thread_slug = thread_slug_or_id
            thread = self._thread_service.get_by_slug(thread_slug)

        if not thread:
            raise NoDataFoundError(f"Can't find thread by slug = {thread_slug}")

        prepare_data = {
            'thread_id': thread.uid,
            'forum_id': thread.forum.uid
        }

        return prepare_data

    def _get_user_id(self, data: Dict[str, Any]) -> int:

        nickname = data.get('author')
        if nickname is None:
            logging.error(f"[PostSerializer._get_user_id] Bad request")
            raise NoDataFoundError(f"Bad request")

        author = self._userService.get_by_nickname(nickname)
        if not author:
            logging.error(f"[PostSerializer.load] Can't find author for thread by nickname = {nickname}")
            raise NoDataFoundError(f"Can't find author for thread by nickname = {nickname}")

        return author.uid

    def _get_parent_id(self, data: Dict[str, Any]) -> int:

        parent_id = data.get('parent')
        # TODO raise another exception
        try:
            cast_parent_id = int(parent_id)  # try cast parent_id to int
        except ValueError as exp:
            logging.error(f"[PostSerializer._get_parent_id] Bad request")
            raise NoDataFoundError(f"Bad request") from exp

        if cast_parent_id != 0:
            parent = self._post_service.get_by_id(cast_parent_id)
            if not parent:
                logging.error(f"[PostSerializer._get_parent_id] Can't find parent for post by uid = {cast_parent_id}")
                raise NoDataFoundError(f"Can't find parent for post by uid = {cast_parent_id}")
            return parent.uid
        else:
            return cast_parent_id

    def load(self, data: Dict[str, Any]) -> PostDTO:

        logging.info(f"[PostSerializer.load] Try load entity")

        post_id = None if data.get('id') is None or data.get('id') == 'null' else data['id']
        user_id = self._get_user_id(data)
        parent_id = self._get_parent_id(data)
        thread_id = None if data.get('thread_id') is None or data.get('thread_id') == 'null' else dateutil.parser.parse(data['thread_id'])
        forum_id = None if data.get('forum_id') is None or data.get('forum_id') == 'null' else dateutil.parser.parse(data['forum_id'])
        created = None if data.get('created') is None or data.get('created') == 'null' else dateutil.parser.parse(data['created'])
        message = None if data.get('message') is None or data.get('message') == 'null' else data['message']
        is_edited = None if data.get('is_edited') is None or data.get('is_edited') == 'null' else data['is_edited']

        return PostDTO(uid=post_id, thread_id=thread_id, forum_id=forum_id, user_id=user_id,
                       parent_id=parent_id, message=message, created=created, is_edited=is_edited)
