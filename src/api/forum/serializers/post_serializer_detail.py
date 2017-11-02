from typing import Dict, Any, Optional

import pytz as pytz
from injector import inject, singleton

from apiutils import Serializer


from forum.models.post import Post
from forum.persistence.dto.post_dto import PostDTO
from forum.serializers.forum_serializer import ForumSerializer
from forum.serializers.post_serializer import PostSerializer
from forum.serializers.thread_serializer import ThreadSerializer
from forum.serializers.user_serializer import UserSerializer
from forum.services.forum_service import ForumService
from forum.services.thread_service import ThreadService
from forum.services.user_service import UserService


@singleton
class PostSerializerFull(Serializer):

    @inject
    def __init__(self, post_serializer: PostSerializer,
                 user_service: UserService, user_serializer: UserSerializer,
                 forum_service: ForumService, forum_serializer: ForumSerializer,
                 thread_service: ThreadService, thread_serializer: ThreadSerializer) -> None:

        self._postSerializer = post_serializer

        self._userService = user_service
        self._forumService = forum_service
        self._threadService = thread_service

        self._userSerializer = user_serializer
        self._forumSerializer = forum_serializer
        self._threadSerializer = thread_serializer

        self._tz = pytz.timezone('Europe/Moscow')

    def dump(self, model: Post, **kwargs) -> Optional[Dict[str, Any]]:

        if not model:
            return None

        data = {}

        if model.is_loaded:

            related = kwargs.get('related')
            if related is not None:

                if 'user' in related:
                    author = self._userService.get_by_id(model.author.uid)
                    data.update({
                        'author': self._userSerializer.dump(author)
                    })

                if 'thread' in related:
                    thread = self._threadService.get_by_id(model.thread.uid)
                    data.update({
                        'thread': thread
                    })

                if 'forum' in related:
                    forum = self._forumService.get_by_id(model.forum.uid)
                    data.update({
                        'forum': self._forumSerializer.dump(forum, expand_details=True)
                    })

            data.update({
                'post': self._postSerializer.dump(model)
            })

        return data

    def prepare_load_data(self, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError

    def load(self, data: Dict[str, Any]) -> PostDTO:
        raise NotImplementedError
