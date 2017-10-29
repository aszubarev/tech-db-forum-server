from typing import Optional, List

from injector import inject

from forum.persistence.dto.vote_dto import VoteDTO
from sqlutils import DataContext, Repository, create_one, create_many

from forum.persistence.dto.thread_dto import ThreadDTO


class ThreadRepository(Repository[ThreadDTO]):

    @inject
    def __init__(self, context: DataContext) -> None:
        self._context = context

    def get_by_id(self, uid: int) -> Optional[ThreadDTO]:
        data = self._context.callproc('get_thread_by_id', [uid])
        return create_one(ThreadDTO, data)

    def get_by_slug(self, slug: str) -> Optional[ThreadDTO]:
        data = self._context.callproc('get_thread_by_slug', [slug])
        return create_one(ThreadDTO, data)

    def get_by_id_setup(self, uid: int, load_forum: bool) -> Optional[ThreadDTO]:

        if load_forum is True:
            data = self._context.callproc('get_thread_by_id_ret_uid_forum', [uid])

        else:
            data = self._context.callproc('get_thread_by_id_ret_uid', [uid])

        return create_one(ThreadDTO, data)

    def get_by_slug_setup(self, slug: str, load_forum: bool) -> Optional[ThreadDTO]:

        if load_forum is True:
            data = self._context.callproc('get_thread_by_slug_ret_uid_forum', [slug])

        else:
            data = self._context.callproc('get_thread_by_slug_ret_uid', [slug])

        return create_one(ThreadDTO, data)

    def get_for_forum(self, forum_id: int, **kwargs) -> List[ThreadDTO]:

        data = None
        desc = kwargs.get('desc')
        limit = kwargs.get('limit')
        since = kwargs.get('since')
        params = [p for p in [forum_id, desc, limit, since] if p is not None]

        if desc is not None and limit is not None and since is not None:
            data = self._context.callproc('get_threads_for_forum_sort_limit_since', params)

        elif desc is not None and limit is not None and since is None:
            data = self._context.callproc('get_threads_for_forum_sort_limit', params)

        elif desc is not None and limit is None and since is None:
            data = self._context.callproc('get_threads_for_forum_sort', params)

        elif desc is None and limit is not None and since is not None:
            data = self._context.callproc('get_threads_for_forum_limit_since', params)

        elif desc is None and limit is not None and since is None:
            data = self._context.callproc('get_threads_for_forum_limit', params)

        elif desc is None and limit is None and since is None:
            data = self._context.callproc('get_threads_for_forum', params)

        return create_many(ThreadDTO, data)

    def get_number_threads_for_forum(self, forum_id: int) -> int:
        data = self._context.callproc('get_number_threads_for_forum', [forum_id])
        if data is None or len(data) == 0:
            return 0
        result_dict = data[0]
        return result_dict.get('number_threads')

    def get_count(self) -> int:
        data = self._context.callproc('get_threads_count', [])
        if data is None or len(data) == 0:
            return 0
        result_dict = data[0]
        return result_dict.get('threads_count')

    def clear(self):
        self._context.callproc('clear_threads', [])

    def get_all(self) -> List[ThreadDTO]:
        raise NotImplementedError

    def vote(self, entity: VoteDTO) -> Optional[int]:
        data = self._context.callproc('add_vote', [entity.user_id, entity.thread_id, entity.vote_value])
        if data is None or len(data) == 0:
            return None
        result_dict = data[0]
        return result_dict.get('votes')

    def add(self, entity: ThreadDTO) -> Optional[ThreadDTO]:
        data = self._context.callproc('add_thread', [entity.slug, entity.forum_id, entity.user_id,
                                                     entity.created, entity.message, entity.title])
        new_entity = create_one(ThreadDTO, data)
        new_entity.user_nickname = entity.user_nickname
        new_entity.forum_slug = entity.forum_slug
        new_entity.votes = 0

        return new_entity

    def add_many(self, entities: List[ThreadDTO]):
        raise NotImplementedError

    def update_by_slug(self, entity: ThreadDTO) -> Optional[ThreadDTO]:
        msg = entity.message
        title = entity.title

        data = None
        if msg is not None and title is not None:
            data = self._context.callproc('update_thread_by_slug_by_msg_title', [entity.slug, msg, title])

        elif msg is not None and title is None:
            data = self._context.callproc('update_thread_by_slug_by_msg', [entity.slug, msg])

        elif msg is None and title is not None:
            data = self._context.callproc('update_thread_by_slug_by_title', [entity.slug, title])

        new_entity = create_one(ThreadDTO, data)
        return new_entity

    def update_by_uid(self, entity: ThreadDTO) -> Optional[ThreadDTO]:
        msg = entity.message
        title = entity.title

        data = None
        if msg is not None and title is not None:
            data = self._context.callproc('update_thread_by_uid_by_msg_title', [entity.uid, msg, title])

        elif msg is not None and title is None:
            data = self._context.callproc('update_thread_by_uid_by_msg', [entity.uid, msg])

        elif msg is None and title is not None:
            data = self._context.callproc('update_thread_by_uid_by_title', [entity.uid, title])

        return create_one(ThreadDTO, data)

    def update(self, entity: ThreadDTO):
        raise NotImplementedError

    def delete(self, uid: int) -> None:
        raise NotImplementedError
