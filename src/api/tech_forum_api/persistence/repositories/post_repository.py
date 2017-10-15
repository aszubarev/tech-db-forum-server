import logging
from typing import Optional, List

from injector import inject
from sqlutils import DataContext, Repository, create_one, create_many

from tech_forum_api.persistence.dto.post_dto import PostDTO


class PostRepository(Repository[PostDTO]):

    @inject
    def __init__(self, context: DataContext) -> None:
        self._context = context

    def get_by_id(self, uid: int) -> Optional[PostDTO]:
        data = self._context.callproc('get_thread_by_id', [uid])
        return create_one(PostDTO, data)

    def get_all(self) -> List[PostDTO]:
        raise NotImplementedError

    def add(self, entities: List[PostDTO]) -> List[PostDTO]:
        if not entities:
            return []

        data_list = []
        for entity in entities:
            data = self._context.callproc('add_post', [entity.thread_id, entity.forum_id, entity.user_id,
                                                       entity.parent_id, entity.message, entity.created])
            data_list.append(data)

        return create_many(PostDTO, data_list)

    def update(self, entity: PostDTO):
        raise NotImplementedError

    def delete(self, uid: int) -> None:
        raise NotImplementedError
