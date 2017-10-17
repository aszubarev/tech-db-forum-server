import logging
from typing import Optional, List

from injector import inject
from sqlutils import DataContext, Repository, create_one, create_many

from tech_forum_api.persistence.dto.vote_dto import VoteDTO


class VoteRepository(Repository[VoteDTO]):

    @inject
    def __init__(self, context: DataContext) -> None:
        self._context = context

    def get_by_id(self, uid: int) -> Optional[VoteDTO]:
        data = self._context.callproc('get_vote_by_id', [uid])
        return create_one(VoteDTO, data)

    def get_for_thread(self, thread_id: int) -> List[VoteDTO]:
        data = self._context.callproc('get_vote_for_thread', [thread_id])
        return create_many(VoteDTO, data)

    def get_all(self) -> List[VoteDTO]:
        raise NotImplementedError

    def add(self, entity: VoteDTO) -> Optional[VoteDTO]:
        logging.info(f"[VoteRepository.add] user_id = {entity.user_id}, thread_id = {entity.thread_id}, "
                     f"voice = {entity.vote_value}")
        data = self._context.callproc('add_vote', [entity.user_id, entity.thread_id, entity.vote_value])
        return create_one(VoteDTO, data)

    def update(self, entity: VoteDTO) -> Optional[VoteDTO]:
        raise NotImplementedError

    def delete(self, uid: int) -> None:
        raise NotImplementedError
