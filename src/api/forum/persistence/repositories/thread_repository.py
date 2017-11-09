from typing import Optional, List, Any, Dict
from injector import inject, singleton
from sqlutils import DataContext, return_one


@singleton
class ThreadRepository(object):

    @inject
    def __init__(self, context: DataContext) -> None:
        self._context = context

    def get_by_id(self, uid: int) -> Optional[Dict[str, Any]]:
        data = self._context.callproc('get_thread_by_id', [uid])
        response = return_one(data)
        if not response:
            return None
        response['created'] = response['created'].astimezone().isoformat()
        return response

    def get_by_slug(self, slug) -> Optional[Dict[str, Any]]:
        data = self._context.callproc('get_thread_by_slug', [slug])
        response = return_one(data)
        if not response:
            return None
        response['created'] = response['created'].astimezone().isoformat()
        return response

    def get_by_slug_or_id(self, slug_or_id: str) -> Optional[Dict[str, Any]]:
        try:
            cast_thread_id = int(slug_or_id)
            thread = self.get_by_id(cast_thread_id)

        except ValueError:
            thread_slug = slug_or_id
            thread = self.get_by_slug(thread_slug)

        return thread

    def get_for_forum(self, forum_id: int, **kwargs) -> List[Dict[str, Any]]:

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

        if not data:
            return []

        for thread in data:
            thread['created'] = thread['created'].astimezone().isoformat()

        return data

    def get_count(self) -> int:
        data = self._context.callproc('get_threads_count', [])
        if data is None or len(data) == 0:
            return 0
        result_dict = data[0]
        return result_dict.get('threads_count')

    def clear(self):
        self._context.callproc('clear_threads', [])

    def vote(self, user_id: int, thread_id: int, voice: int) -> Optional[int]:
        data = self._context.callproc('add_vote', [user_id, thread_id, voice])
        result_dict = data[0]
        votes = result_dict.get('votes')
        return votes

    def add(self, params: Dict[str, Any]) -> Dict[str, Any]:

        data = self._context.callproc('add_thread', [params['slug'],     # must be init in blueprint
                                                     params['forum_id'], params['forum_slug'],
                                                     params['user_id'], params['user_nickname'],
                                                     params['created'],  # must be init in blueprint
                                                     params['message'], params['title']])
        thread_id = data[0]['thread_id']
        response = {
            'id': thread_id,
            'forum': params['forum_slug'],
            'author': params['user_nickname'],
            'message': params['message'],
            'title': params['title'],
            'votes': 0
        }

        if params['created'] is not None:
            response['created'] = params['created'].astimezone().isoformat()

        if params['slug'] is not None:
            response['slug'] = params['slug']

        return response

    def update_by_slug(self, slug: str, msg: str = None, title: str = None) -> Optional[Dict[str, Any]]:

        data = None
        if msg is not None and title is not None:
            data = self._context.callproc('update_thread_by_slug_by_msg_title', [slug, msg, title])

        elif msg is not None and title is None:
            data = self._context.callproc('update_thread_by_slug_by_msg', [slug, msg])

        elif msg is None and title is not None:
            data = self._context.callproc('update_thread_by_slug_by_title', [slug, title])

        response = return_one(data)
        if not response:
            return None
        response['created'] = response['created'].astimezone().isoformat()
        return response

    def update_by_uid(self, uid: int, msg: str = None, title: str = None) -> Optional[Dict[str, Any]]:

        data = None
        if msg is not None and title is not None:
            data = self._context.callproc('update_thread_by_uid_by_msg_title', [uid, msg, title])

        elif msg is not None and title is None:
            data = self._context.callproc('update_thread_by_uid_by_msg', [uid, msg])

        elif msg is None and title is not None:
            data = self._context.callproc('update_thread_by_uid_by_title', [uid, title])

        response = return_one(data)
        if not response:
            return None
        response['created'] = response['created'].astimezone().isoformat()
        return response

    def update_by_slug_or_id(self, slug_or_id: str, msg: str = None, title: str = None):
        try:

            cast_thread_id = int(slug_or_id)
            thread = self.update_by_uid(uid=cast_thread_id, msg=msg, title=title)

        except ValueError:
            thread_slug = slug_or_id
            thread = self.update_by_slug(slug=thread_slug, msg=msg, title=title)

        return thread
