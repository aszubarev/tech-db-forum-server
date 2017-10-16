from sqlutils import Converter
from tech_forum_api.models.thread import Thread
from tech_forum_api.models.user import User

from tech_forum_api.models.vote import Vote
from tech_forum_api.persistence.dto.vote_dto import VoteDTO


class VoteConverter(Converter[Vote, VoteDTO]):

    def convert(self, entity: VoteDTO) -> Vote:
        return Vote(uid=entity.uid).fill(
            user=User(entity.user_id),
            thread=Thread(entity.thread_id),
            vote_value=entity.vote_value
        )
