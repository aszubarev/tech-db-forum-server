from typing import Optional, List

from injector import inject
from sqlutils import DataContext, Repository, create_one, create_many

from tech_forum_api.persistence.dto.forum_dto import ForumDTO


class ForumRepository(Repository[ForumDTO]):

    @inject
    def __init__(self, context: DataContext) -> None:
        self._context = context

    def get_by_id(self, uid: int) -> Optional[ForumDTO]:
        data = self._context.callproc('get_forum_by_id', [uid])
        return create_one(ForumDTO, data)

    def get_by_slug(self, slug: str) -> Optional[ForumDTO]:
        data = self._context.callproc('get_forum_by_slug', [slug])
        return create_one(ForumDTO, data)

    def get_by_thread_id(self, thread_id: int) -> Optional[ForumDTO]:
        data = self._context.callproc('get_forum_by_slug', [thread_id])
        return create_one(ForumDTO, data)

    def get_count(self) -> int:
        data = self._context.callproc('get_forums_count', [])
        if data is None or len(data) == 0:
            return 0
        result_dict = data[0]
        return result_dict.get('forums_count')

    def clear(self):
        self._context.callproc('clear_forums', [])

    def get_all(self) -> List[ForumDTO]:
        raise NotImplementedError

    def add(self, entity: ForumDTO) -> Optional[ForumDTO]:
        data = self._context.callproc('add_forum', [entity.slug, entity.user_id, entity.title])
        return create_one(ForumDTO, data)

    def update(self, entity: ForumDTO):
        raise NotImplementedError

    def delete(self, uid: int) -> None:
        raise NotImplementedError
