import logging
from typing import Optional, List

from injector import inject
from sqlutils import DataContext, Repository, create_one, create_many

from tech_forum_api.persistence.dto.thread_dto import ThreadDTO


class ThreadRepository(Repository[ThreadDTO]):

    @inject
    def __init__(self, context: DataContext) -> None:
        self._context = context

    def get_by_id(self, uid: int) -> Optional[ThreadDTO]:
        data = self._context.callproc('get_thread_by_id', [uid])
        return create_one(ThreadDTO, data)

    def get_all(self) -> List[ThreadDTO]:
        raise NotImplementedError

    def add(self, entity: ThreadDTO) -> Optional[ThreadDTO]:

        logging.info(f"[ThreadRepository.add] slug = {entity.slug}; forum_id = {entity.forum_id}, user_id = {entity.user_id}")
        logging.info(f"[ThreadRepository.add] created = {entity.created}; title = {entity.title}")

        data = self._context.callproc('add_thread', [entity.slug, entity.forum_id, entity.user_id,
                                                     entity.created, entity.message, entity.title])
        return create_one(ThreadDTO, data)

    def update(self, entity: ThreadDTO):
        raise NotImplementedError

    def delete(self, uid: int) -> None:
        raise NotImplementedError
