import logging
from datetime import datetime
from typing import Dict, Any, Optional

import dateutil.parser
import pytz as pytz
from injector import inject, singleton

from apiutils import Serializer
from apiutils.errors.bad_request_error import BadRequestError
from apiutils.errors.server_error import ServerError

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

    def dump(self, model: Post, **kwargs) -> Optional[Dict[str, Any]]:

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
                'thread': model.thread.uid,
                'message': model.message,
                'isEdited': model.is_edited

            })

            if model.created is not None:
                data.update({
                    'created': model.created.astimezone().isoformat()
                })

        return data

    def prepare_load_data(self, **kwargs) -> Dict[str, Any]:

        thread_slug_or_id = kwargs.get('thread_slug_or_id')

        if thread_slug_or_id is None:
            raise ServerError(f"Can't get parameter 'thread_slug_or_id'")

        try:
            cast_thread_id = int(thread_slug_or_id)
            thread = self._thread_service.get_by_id(cast_thread_id)

        except ValueError:
            thread_slug = thread_slug_or_id
            thread = self._thread_service.get_by_slug(thread_slug)

        if not thread:
            raise NoDataFoundError(f"Can't find thread by thread_slug_or_id = {thread_slug_or_id}")

        prepare_data = {
            'thread_id': thread.uid,
            'forum_id': thread.forum.uid
        }

        logging.info(f"[PostSerializer.prepare_load_data] Complete prepare load data")

        return prepare_data

    def _get_user_id(self, data: Dict[str, Any]) -> int:

        nickname = data.get('author')
        if nickname is None:
            raise BadRequestError(f"Can't get parameter 'nickname'")

        author = self._userService.get_by_nickname(nickname)
        if not author:
            raise NoDataFoundError(f"Can't find author by nickname = {nickname}")

        return author.uid

    def _get_parent_id(self, data: Dict[str, Any]) -> int:

        parent_id = data.get('parent')
        if parent_id is None:
            return 0

        try:
            cast_parent_id = int(parent_id)  # try cast parent_id to int
        except ValueError as exp:
            raise BadRequestError(f"Bad request") from exp

        if cast_parent_id != 0:
            parent = self._post_service.get_by_id(cast_parent_id)
            if not parent:
                raise NoDataFoundError(f"Can't find parent for post by uid = {cast_parent_id}")
            return parent.uid
        else:
            return 0

    def load(self, data: Dict[str, Any]) -> PostDTO:

        post_id = None if data.get('id') is None or data.get('id') == 'null' else data['id']
        user_id = self._get_user_id(data)
        parent_id = self._get_parent_id(data)
        thread_id = None if data.get('thread_id') is None or data.get('thread_id') == 'null' else data['thread_id']
        forum_id = None if data.get('forum_id') is None or data.get('forum_id') == 'null' else data['forum_id']
        created = datetime.now(tz=pytz.utc) if data.get('created') is None or data.get('created') == 'null' else dateutil.parser.parse(data['created'])
        message = None if data.get('message') is None or data.get('message') == 'null' else data['message']
        is_edited = None if data.get('is_edited') is None or data.get('is_edited') == 'null' else data['is_edited']

        return PostDTO(uid=post_id, thread_id=thread_id, forum_id=forum_id, user_id=user_id,
                       parent_id=parent_id, message=message, created=created, is_edited=is_edited)
