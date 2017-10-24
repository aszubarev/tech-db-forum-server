import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

import dateutil.parser
import pytz as pytz
from injector import inject, singleton

from apiutils import Serializer
from apiutils.errors.bad_request_error import BadRequestError
from apiutils.errors.server_error import ServerError
from forum.exceptions.post_invalid_parent import PostInvalidParentError

from forum.models.post import Post
from forum.persistence.dto.post_dto import PostDTO
from forum.serializers.forum_serializer import ForumSerializer
from forum.serializers.thread_serializer import ThreadSerializer
from forum.serializers.user_serializer import UserSerializer
from forum.services.forum_service import ForumService
from forum.services.post_service import PostService
from forum.services.thread_service import ThreadService
from forum.services.user_service import UserService
from sqlutils import NoDataFoundError


@singleton
class PostSerializer(Serializer):

    @inject
    def __init__(self, post_service: PostService,
                 user_service: UserService, user_serializer: UserSerializer,
                 forum_service: ForumService, forum_serializer: ForumSerializer,
                 thread_service: ThreadService, thread_serializer: ThreadSerializer) -> None:

        self._post_service = post_service

        self._userService = user_service
        self._forum_service = forum_service
        self._thread_service = thread_service

        self._user_serializer = user_serializer
        self._forum_serializer = forum_serializer
        self._thread_serializer = thread_serializer

        self._tz = pytz.timezone('Europe/Moscow')

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
                    'created':  model.created.astimezone(tz=self._tz).isoformat()
                })

            if model.parent.uid != 0:
                data.update({
                    'parent': model.parent.uid
                })

        return data

    def prepare_load_data(self, **kwargs) -> Dict[str, Any]:

        thread_slug_or_id = kwargs.get('thread_slug_or_id')

        if thread_slug_or_id is None:
            raise ServerError(f"Can't get parameter 'thread_slug_or_id'")

        thread = self._thread_service.get_by_slug_or_id(thread_slug_or_id)
        if not thread:
            logging.error(f"[PostSerializer.prepare_load_data] thread is None")
            raise NoDataFoundError(f"[PostSerializer.prepare_load_data] thread is None \n"
                                   f" Can't find thread by thread_slug_or_id = {thread_slug_or_id}")

        else:
            logging.error(f"[PostSerializer.prepare_load_data] thread is not None; "
                          f"thread_slug_or_id = {thread_slug_or_id}\n")

        created = kwargs.get('created')
        if not created:
            created = datetime.now(tz=self._tz).astimezone(tz=self._tz).isoformat()

        prepare_data = {
            'thread_id': thread.uid,
            'forum_id': thread.forum.uid,
            'created': created
        }

        return prepare_data

    def _get_user_id(self, data: Dict[str, Any]) -> Optional[int]:

        nickname = data.get('author')
        if nickname is None:
            return None

        author = self._userService.get_by_nickname(nickname)
        if not author:
            raise NoDataFoundError(f"Can't find author by nickname = {nickname}")

        return author.uid

    def _get_parent(self, data: Dict[str, Any]) -> Post:

        parent_id = data.get('parent')
        if parent_id is None:
            return Post(uid=0)

        try:
            cast_parent_id = int(parent_id)  # try cast parent_id to int
        except ValueError as exp:
            raise BadRequestError(f"Bad request") from exp

        if cast_parent_id != 0:
            parent = self._post_service.get_by_id(cast_parent_id)
            if not parent:
                raise PostInvalidParentError(f"Can't find parent for post by uid = {cast_parent_id}")
            return parent
        else:
            return Post(uid=0)

    # TODO move declaration of user_id and parent_id to upper level
    def load(self, data: Dict[str, Any]) -> PostDTO:

        post_id = None if data.get('id') is None or data.get('id') == 'null' else data['id']
        user_id = self._get_user_id(data)

        parent = self._get_parent(data)
        parent_id = parent.uid

        thread_id = None if data.get('thread_id') is None else data['thread_id']
        if parent.thread is not None and thread_id is not None:
            if parent.thread.uid != thread_id:
                raise PostInvalidParentError(f"Parent post was created in another thread: uid = {parent.thread.uid}")

        forum_id = None if data.get('forum_id') is None else data['forum_id']
        created = None if data.get('created') is None else dateutil.parser.parse(data['created'])
        message = None if data.get('message') is None else data['message']
        is_edited = None if data.get('is_edited') is None else data['is_edited']

        return PostDTO(uid=post_id, thread_id=thread_id, forum_id=forum_id, user_id=user_id,
                       parent_id=parent_id, message=message, created=created, is_edited=is_edited)
