from typing import Dict, Any

from injector import inject, singleton

from apiutils import Serializer

from forum.models.vote import Vote
from forum.persistence.dto.vote_dto import VoteDTO


@singleton
class VoteSerializer(Serializer):

    @inject
    def __init__(self) -> None:
        pass

    def dump(self, model: Vote, **kwargs):
        raise NotImplementedError

    def prepare_load_data(self, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError

    def load(self, data: Dict[str, Any]) -> VoteDTO:

        vote_id = None if data.get('id') is None else int(data['id'])
        user_id = None if data.get('user_id') is None else int(data['user_id'])
        thread_id = None if data.get('thread_id') is None else int(data['thread_id'])
        vote_value = None if data.get('voice') is None else int(data['voice'])
        return VoteDTO(uid=vote_id, user_id=user_id, thread_id=thread_id, vote_value=vote_value)
