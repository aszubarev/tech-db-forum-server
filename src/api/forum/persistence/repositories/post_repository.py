from typing import Optional, List, Dict, Any

import pytz
from injector import inject, singleton

from sqlutils import DataContext, return_one


@singleton
class PostRepository(object):

    @inject
    def __init__(self, context: DataContext) -> None:
        self._context = context
        self._tz = pytz.timezone('Europe/Moscow')

    def get_by_id(self, uid: int) -> Optional[Dict[str, Any]]:
        data = self._context.callproc('get_post_by_id', [uid])
        if not data:
            return None
        response = return_one(data)
        if not response:
            return None

        response['created'] = response['created'].astimezone(self._tz).isoformat()
        response['isEdited'] = response['isedited']
        del response['isedited']

        return response

    def get_parent(self, uid: int) -> Optional[Dict[str, Any]]:
        data = self._context.callproc('get_parent_post_by_id', [uid])
        return return_one(data)

    def get_posts_for_thread(self, thread_id: int, **kwargs) -> List[Dict[str, Any]]:
        sort = kwargs.get('sort')
        limit = kwargs.get('limit')
        since = kwargs.get('since')
        desc = kwargs.get('desc')

        data = None

        # FLAT SORT or EMPTY SORT
        if sort == 'flat' or sort is None:
            if limit is not None and since is None and desc is None:
                data = self._context.callproc('get_posts_for_thread_flat_limit', [thread_id, limit])

            elif limit is not None and since is None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_flat_limit_desc', [thread_id, limit, desc])

            elif limit is not None and since is not None and desc is None:
                data = self._context.callproc('get_posts_for_thread_flat_since_limit', [thread_id, since, limit])

            elif limit is not None and since is not None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_flat_since_limit_desc',
                                              [thread_id, since, limit, desc])

            elif limit is None and since is None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_flat_desc', [thread_id, desc])

            elif limit is None and since is None and desc is None:
                data = self._context.callproc('get_posts_for_thread_flat', [thread_id])

        # TREE SORT
        elif sort == 'tree':
            if limit is not None and since is None and desc is None:
                data = self._context.callproc('get_posts_for_thread_tree_limit', [thread_id, limit])

            elif limit is not None and since is None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_tree_limit_desc', [thread_id, limit, desc])

            elif limit is not None and since is not None and desc is None:
                data = self._context.callproc('get_posts_for_thread_tree_since_limit', [thread_id, since, limit])

            elif limit is not None and since is not None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_tree_since_limit_desc',
                                              [thread_id, since, limit, desc])

            elif limit is None and since is None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_tree_desc', [thread_id, desc])

            elif limit is None and since is None and desc is None:
                data = self._context.callproc('get_posts_for_thread_tree', [thread_id])

        # PARENT_TREE SORT
        # TODO CREATE INDEX for thread_id and parent_id
        elif sort == 'parent_tree':
            if limit is not None and since is None and desc is None:
                data = self._context.callproc('get_posts_for_thread_parent_tree_limit', [thread_id, limit])

            elif limit is not None and since is None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_parent_tree_limit_desc',
                                              [thread_id, limit, desc])

            elif limit is not None and since is not None and desc is None:
                data = self._context.callproc('get_posts_for_thread_parent_tree_since_limit',
                                              [thread_id, since, limit])

            elif limit is not None and since is not None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_parent_tree_since_limit_desc',
                                              [thread_id, since, limit, desc])

            elif limit is None and since is None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_parent_tree_desc', [thread_id, desc])

            elif limit is None and since is None and desc is None:
                data = self._context.callproc('get_posts_for_thread_parent_tree', [thread_id])

        if not data:
            return []

        for post in data:
            post['created'] = post['created'].astimezone(self._tz).isoformat()
            post['isEdited'] = post['isedited']
            del post['isedited']

        return data

    def get_count(self) -> int:
        data = self._context.callproc('get_posts_count', [])
        if data is None or len(data) == 0:
            return 0
        result_dict = data[0]
        return result_dict.get('posts_count')

    def add_many(self, insert_values: str, insert_args: str) -> None:
        self._context.add_many(table='posts', insert_values=insert_values, insert_args=insert_args)

    def update(self, uid: int, message: str):
        data = self._context.callproc('update_post_soft', [uid, message])
        response = return_one(data)
        if not response:
            return None
        response['created'] = response['created'].astimezone(self._tz).isoformat()
        response['isEdited'] = response['isedited']     # WTF??? why should I do this?
        del response['isedited']                        # WTF??? why should I do this?
        return response

    def clear(self):
        self._context.callproc('clear_posts', [])

    def next_uid(self) -> Optional[int]:
        data = self._context.execute("SELECT nextval('posts_post_id_seq');", {})
        if data is None or len(data) == 0:
            return None
        result_dict = data[0]
        return result_dict.get('nextval')
