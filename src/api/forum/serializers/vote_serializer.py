from typing import Dict, Any, Optional

from injector import inject, singleton

from apiutils import Serializer

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

        vote_id = None if data.get('id') is None else int(data['id'])
        user_id = None if data.get('user_id') is None else int(data['user_id'])
        thread_id = None if data.get('thread_id') is None else int(data['thread_id'])
        vote_value = None if data.get('voice') is None else int(data['voice'])
        return VoteDTO(uid=vote_id, user_id=user_id, thread_id=thread_id, vote_value=vote_value)
