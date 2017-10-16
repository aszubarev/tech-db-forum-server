import logging
from typing import Dict, Any, Optional

from injector import inject, singleton

from apiutils import Serializer

from tech_forum_api.models.vote import Vote
from tech_forum_api.persistence.dto.vote_dto import VoteDTO


@singleton
class VoteSerializer(Serializer):

    @inject
    def __init__(self):
        pass

    def dump(self, model: Vote) -> Optional[Dict[str, Any]]:

        if not model:
            return None

        data = {}

        if model.is_loaded:
            data.update({
            })

        return data

    def prepare_load_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {}

    def load(self, data: Dict[str, Any]) -> VoteDTO:
        vote_id = None if data.get('id') is None or data.get('id') == 'null' else int(data['id'])
        user_id = None if data.get('user_id') is None or data.get('user_id') == 'null' else data['user_id']
        thread_id = None if data.get('thread_id') is None or data.get('thread_id') == 'null' else data['thread_id']
        vote_value = None if data.get('voice') is None or data.get('voice') == 'null' else data['voice']
        return VoteDTO(uid=vote_id, user_id=user_id, thread_id=thread_id, vote_value=vote_value)
