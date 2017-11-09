from typing import Optional, List, Any, Dict

from injector import inject, singleton
from sqlutils import DataContext, return_one


@singleton
class UserRepository(object):

    @inject
    def __init__(self, context: DataContext) -> None:
        self._context = context

    def get_by_id(self, uid: int) -> Optional[Dict[str, Any]]:
        data = self._context.callproc('get_user_by_id', [uid])
        return return_one(data)

    def get_by_nickname(self, nickname: str) -> Optional[Dict[str, Any]]:
        data = self._context.callproc('get_user_by_nickname', [nickname])
        return return_one(data)

    def get_by_nickname_or_email(self, nickname: str, email: str) -> List[Dict[str, Any]]:
        data = self._context.callproc('get_users_by_nickname_or_email', [nickname, email])
        return data

    def get_for_forum(self, forum_id: int, since: str, limit: str, desc: str) -> List[Dict[str, Any]]:
        data = None

        if since is not None and limit is None and desc is None:
            data = self._context.callproc('get_users_for_forum_since', [forum_id, since])

        elif since is None and limit is not None and desc is None:
            data = self._context.callproc('get_users_for_forum_limit', [forum_id, limit])

        elif since is None and limit is None and desc is not None:
            data = self._context.callproc('get_users_for_forum_desc', [forum_id, desc])

        elif since is None and limit is not None and desc is not None:
            data = self._context.callproc('get_users_for_forum_limit_desc', [forum_id, limit, desc])

        elif since is not None and limit is not None and desc is None:
            data = self._context.callproc('get_users_for_forum_since_limit', [forum_id, since, limit])

        elif since is not None and limit is None and desc is not None:
            data = self._context.callproc('get_users_for_forum_since_desc', [forum_id, since, desc])

        elif since is not None and limit is not None and desc is not None:
            data = self._context.callproc('get_users_for_forum_since_limit_desc', [forum_id, since, limit, desc])

        elif since is None and limit is None and desc is None:
            data = self._context.callproc('get_users_for_forum', [forum_id])

        return data

    def get_count(self) -> int:
        data = self._context.callproc('get_users_count', [])
        if data is None or len(data) == 0:
            return 0
        result_dict = data[0]
        return result_dict.get('users_count')

    def clear(self):
        self._context.callproc('clear_users', [])

    def add(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        self._context.callproc('add_user', [params['nickname'], params['email'], params['about'], params['fullname']])
        return params

    def update(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:

        data = None
        nickname = params['nickname']
        email = params.get('email')
        about = params.get('about')
        fullname = params.get('fullname')

        if email is not None and about is not None and fullname is not None:
            data = self._context.callproc('update_user', [nickname, email, about, fullname])

        elif email is not None and about is None and fullname is None:
            data = self._context.callproc('update_user_by_email', [nickname, email])

        elif email is None and about is not None and fullname is None:
            data = self._context.callproc('update_user_by_about', [nickname, about])

        elif email is None and about is None and fullname is not None:
            data = self._context.callproc('update_user_by_fullname', [nickname, fullname])

        elif email is None and about is not None and fullname is not None:
            data = self._context.callproc('update_user_by_about_fullname', [nickname, about, fullname])

        elif email is not None and about is None and fullname is not None:
            data = self._context.callproc('update_user_by_email_fullname', [nickname, email, fullname])

        elif email is not None and about is not None and fullname is None:
            data = self._context.callproc('update_user_by_email_about', [nickname, email, about])

        elif email is None and about is None and fullname is None:
            data = self._context.callproc('update_user_by_empty_data', [nickname])

        return return_one(data)
