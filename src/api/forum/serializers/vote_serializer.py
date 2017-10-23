import logging
from typing import Dict, Any, Optional

from injector import inject, singleton

from apiutils import Serializer
from apiutils.errors.bad_request_error import BadRequestError
from sqlutils import NoDataFoundError

from forum.models.vote import Vote
from forum.persistence.dto.vote_dto import VoteDTO
from forum.serializers.thread_serializer import ThreadSerializer
from forum.services.thread_service import ThreadService
from forum.services.user_service import UserService
from forum.services.vote_service import VoteService


@singleton
class VoteSerializer(Serializer):

    @inject
    def __init__(self, vote_service: VoteService, thread_service: ThreadService,
                 user_service: UserService, thread_serializer: ThreadSerializer) -> None:
        self._vote_service =vote_service
        self._thread_service = thread_service
        self._user_service = user_service
        self._thread_serializer = thread_serializer

    def dump(self, model: Vote, **kwargs) -> Optional[Dict[str, Any]]:

        if not model:
            return None

        data = {}

        if model.is_loaded:
            thread = self._thread_service.get_by_id(model.thread.uid)
            data = self._thread_serializer.dump(thread)
            votes = self._vote_service.votes(thread.uid)

            data.update({
                'votes': votes
            })

        return data

    def prepare_load_data(self, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError

    def load(self, data: Dict[str, Any]) -> VoteDTO:

        # get request parameters
        thread_slug_or_id = data.get('thread_slug_or_id')
        if not thread_slug_or_id:
            raise BadRequestError("[VoteSerializer.load] Can't get param 'thread_slug_or_id'")

        nickname = data.get('nickname')
        if not nickname:
            raise BadRequestError("[VoteSerializer.load] Can't get param 'nickname'")

        voice = data.get('voice')
        if not voice :
            raise BadRequestError("[VoteSerializer.load] Can't get param 'voice'")

        # find user by input nickname
        user = self._user_service.get_by_nickname(nickname)
        if not user:
            raise NoDataFoundError(f"[VoteSerializer.load] Can't find user by nickname = {nickname}")

        # find thread by input slug or id
        try:
            cast_thread_id = int(thread_slug_or_id)
            thread = self._thread_service.get_by_id(cast_thread_id)

        except ValueError:
            thread_slug = thread_slug_or_id
            thread = self._thread_service.get_by_slug(thread_slug)

        if not thread:
            raise NoDataFoundError(f"[VoteSerializer.load] Can't find thread by slug_or_id = {thread_slug_or_id}")

        vote_id = None if data.get('id') is None or data.get('id') == 'null' else int(data['id'])
        user_id = user.uid
        thread_id = thread.uid
        vote_value = voice
        return VoteDTO(uid=vote_id, user_id=user_id, thread_id=thread_id, vote_value=vote_value)
