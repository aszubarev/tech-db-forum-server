from sqlutils import Converter
from forum.models.thread import Thread
from forum.models.user import User

from forum.models.vote import Vote
from forum.persistence.dto.vote_dto import VoteDTO


class VoteConverter(Converter[Vote, VoteDTO]):

    def convert(self, entity: VoteDTO) -> Vote:
        return Vote(uid=entity.uid).fill(
            user=User(entity.user_id),
            thread=Thread(entity.thread_id),
            vote_value=entity.vote_value
        )
