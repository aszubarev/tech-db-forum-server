import logging
from typing import Optional, List, Dict, Any, TypeVar, Type

import pytz
from injector import inject

from forum.models.thread import Thread
from sqlutils import DataContext, Repository, create_one, create_many, return_one, NoDataFoundError

from forum.persistence.dto.post_dto import PostDTO


class PostRepository(Repository[PostDTO]):

    @inject
    def __init__(self, context: DataContext) -> None:
        self._context = context
        self._tz = pytz.timezone('Europe/Moscow')

    def get_by_id(self, uid: int) -> Optional[PostDTO]:
        data = self._context.callproc('get_post_by_id', [uid])
        return create_one(PostDTO, data)

    def get_by_id_setup(self, uid: int, load_path: bool, load_thread: bool) -> Optional[PostDTO]:

        if load_path is True and load_thread is True:
            data = self._context.callproc('get_post_by_id_ret_uid_thread_path', [uid])
        else:
            data = self._context.callproc('get_post_by_id_ret_uid', [uid])

        return create_one(PostDTO, data)

    def get_posts_for_thread(self, thread_id: int, **kwargs) -> List[Dict[str, Any]]:
        sort = kwargs.get('sort')
        limit = kwargs.get('limit')
        since = kwargs.get('since')
        desc = kwargs.get('desc')

        data = None

        # FLAT SORT or EMPTY SORT
        if sort == 'flat' or sort is None:
            if limit is not None and since is None and desc is None:
                data = self._context.callproc('get_posts_for_thread_flat_limit_fix', [thread_id, limit])

            elif limit is not None and since is None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_flat_limit_desc_fix', [thread_id, limit, desc])

            elif limit is not None and since is not None and desc is None:
                data = self._context.callproc('get_posts_for_thread_flat_since_limit_fix', [thread_id, since, limit])

            elif limit is not None and since is not None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_flat_since_limit_desc_fix',
                                              [thread_id, since, limit, desc])

            elif limit is None and since is None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_flat_desc_fix', [thread_id, desc])

            elif limit is None and since is None and desc is None:
                data = self._context.callproc('get_posts_for_thread_flat_fix', [thread_id])

        # TREE SORT
        elif sort == 'tree':
            if limit is not None and since is None and desc is None:
                data = self._context.callproc('get_posts_for_thread_tree_limit_fix', [thread_id, limit])

            elif limit is not None and since is None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_tree_limit_desc_fix', [thread_id, limit, desc])

            elif limit is not None and since is not None and desc is None:
                data = self._context.callproc('get_posts_for_thread_tree_since_limit_fix', [thread_id, since, limit])

            elif limit is not None and since is not None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_tree_since_limit_desc_fix',
                                              [thread_id, since, limit, desc])

            elif limit is None and since is None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_tree_desc_fix', [thread_id, desc])

            elif limit is None and since is None and desc is None:
                data = self._context.callproc('get_posts_for_thread_tree_fix', [thread_id])

        # PARENT_TREE SORT
        # TODO CREATE INDEX for thread_id and parent_id
        elif sort == 'parent_tree':
            if limit is not None and since is None and desc is None:
                data = self._context.callproc('get_posts_for_thread_parent_tree_limit_fix', [thread_id, limit])

            elif limit is not None and since is None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_parent_tree_limit_desc_fix',
                                              [thread_id, limit, desc])

            elif limit is not None and since is not None and desc is None:
                data = self._context.callproc('get_posts_for_thread_parent_tree_since_limit_fix',
                                              [thread_id, since, limit])

            elif limit is not None and since is not None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_parent_tree_since_limit_desc_fix',
                                              [thread_id, since, limit, desc])

            elif limit is None and since is None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_parent_tree_desc_fix', [thread_id, desc])

            elif limit is None and since is None and desc is None:
                data = self._context.callproc('get_posts_for_thread_parent_tree_fix', [thread_id])

        if not data:
            return []

        for post in data:
            post['created'] = post['created'].astimezone().isoformat()

        return data

    def get_number_posts_for_forum(self, forum_id: int) -> int:
        data = self._context.callproc('get_number_posts_for_forum', [forum_id])
        if data is None or len(data) == 0:
            return 0
        result_dict = data[0]
        return result_dict.get('number_posts')

    def get_count(self) -> int:
        data = self._context.callproc('get_posts_count', [])
        if data is None or len(data) == 0:
            return 0
        result_dict = data[0]
        return result_dict.get('posts_count')

    def get_all(self) -> List[PostDTO]:
        raise NotImplementedError

    def clear(self):
        self._context.callproc('clear_posts', [])

    def add(self, entity: PostDTO) -> Optional[PostDTO]:

        uid = self.next_uid()
        if entity.parent_id != 0:
            path = entity.parent_path
            path.append(uid)
        else:
            path = [uid]

        data = self._context.callproc('add_post_new', [uid, entity.thread_id, entity.forum_id, entity.user_id,
                                                       entity.parent_id, entity.message, entity.created.astimezone(tz=self._tz).isoformat(), path])
        new_entity = create_one(PostDTO, data)
        new_entity.user_nickname = entity.user_nickname
        new_entity.forum_slug = entity.forum_slug

        return new_entity

    def add_many(self, insert_values: str, insert_args: str) -> None:
        self._context.add_many(table='posts', insert_values=insert_values, insert_args=insert_args)

    def update(self, entity: PostDTO) -> Optional[PostDTO]:
        data = None
        if entity.message is not None:
            data = self._context.callproc('update_post', [entity.uid, entity.message])
        return create_one(PostDTO, data)

    def delete(self, uid: int) -> None:
        raise NotImplementedError

    def _update_path(self, uid: int, path: List[int]):
        self._context.callproc('update_post_path_by_id', [uid, path])

    def next_uid(self) -> Optional[int]:
        data = self._context.execute("SELECT nextval('posts_post_id_seq');", {})
        if data is None or len(data) == 0:
            return None
        result_dict = data[0]
        return result_dict.get('nextval')

    @staticmethod
    def _create_many(data: List[Dict[str, Any]], thread: Thread) -> List[PostDTO]:
        entities = []
        for row in data:
            entity = PostDTO.create(row)
            entity.forum_slug = thread.forum.slug
            entities.append(entity)
        return entities

