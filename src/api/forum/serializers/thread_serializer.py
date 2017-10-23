import logging
from datetime import datetime
from typing import Dict, Any, Optional

import dateutil.parser
from injector import inject, singleton

from apiutils import Serializer
from apiutils.coverters.datetime_coverter import DatetimeConverter

from forum.models.thread import Thread
from forum.persistence.dto.thread_dto import ThreadDTO
from forum.services.forum_service import ForumService
from forum.services.user_service import UserService
from forum.services.vote_service import VoteService


@singleton
class ThreadSerializer(Serializer):

    @inject
    def __init__(self, user_service: UserService, forum_service: ForumService, vote_service: VoteService):
        self._userService = user_service
        self._forumService = forum_service
        self._voteService = vote_service

    def dump(self, model: Thread, **kwargs) -> Optional[Dict[str, Any]]:

        if not model:
            return None

        data = {}
        author = self._userService.get_by_id(model.author.uid)
        forum = self._forumService.get_by_id(model.forum.uid)
        votes = self._voteService.votes(model.uid)

        if model.is_loaded:
            data.update({
                'id': model.uid,
                'author': author.nickname,
                'forum': forum.slug,
                'message': model.message,
                'title': model.title

            })

            if model.created is not None:
                created = model.created.astimezone().isoformat()
                logging.info(f"[ThreadSerializer.dump] author: {author.nickname},"
                             f" created: {created}")
                data.update({
                    'created': created
                })

            if model.slug is not None:
                data.update({
                    'slug': model.slug
                })

            if votes is not None and votes != 0:
                data.update({
                    'votes': votes
                })

        return data

    def prepare_load_data(self, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError

    def load(self, data: Dict[str, Any]) -> ThreadDTO:

        thread_id = None if data.get('id') is None else data['id']
        slug = None if data.get('slug') is None else data['slug']
        forum_id = None if data.get('forum_id') is None else data['forum_id']
        user_id = None if data.get('author_id') is None else data['author_id']
        created = None if data.get('created') is None else dateutil.parser.parse(data['created'])
        message = None if data.get('message') is None else data['message']
        title = None if data.get('title') is None else data['title']

        return ThreadDTO(uid=thread_id, slug=slug, forum_id=forum_id,
                         user_id=user_id, created=created, message=message, title=title)
