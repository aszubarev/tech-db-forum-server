from typing import Optional, List, Any, Dict

from injector import inject
from sqlutils import DataContext, create_one, create_many, return_one, return_many

from forum.persistence.dto.user_dto import UserDTO


class UserRepository(object):

    @inject
    def __init__(self, context: DataContext) -> None:
        self._context = context

    def get_by_id(self, uid: int) -> Optional[UserDTO]:
        data = self._context.callproc('get_user_by_id', [uid])
        return create_one(UserDTO, data)

    # TODO DEPRECATED
    def get_by_nickname(self, nickname: str) -> Optional[UserDTO]:
        data = self._context.callproc('get_user_by_nickname', [nickname])
        return create_one(UserDTO, data)

    def get_by_nickname_soft(self, nickname: str) -> Optional[Dict[str, Any]]:
        data = self._context.callproc('get_user_by_nickname', [nickname])
        return return_one(data)

    def get_by_nickname_setup(self, nickname: str, load_nickname: bool) -> Optional[UserDTO]:

        if load_nickname is True:
            data = self._context.callproc('get_by_nickname_ret_uid_nickname', [nickname])
        else:
            data = self._context.callproc('get_by_nickname_ret_uid', [nickname])

        return create_one(UserDTO, data)

    def get_by_nickname_or_email(self, nickname: str, email: str) -> List[UserDTO]:
        data = self._context.callproc('get_users_by_nickname_or_email', [nickname, email])
        return create_many(UserDTO, data)

    def get_for_forum(self, forum_id: int, **kwargs) -> List[UserDTO]:

        data = None
        desc = kwargs.get('desc')
        limit = kwargs.get('limit')
        since = kwargs.get('since')

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

        return create_many(UserDTO, data)

    def get_count(self) -> int:
        data = self._context.callproc('get_users_count', [])
        if data is None or len(data) == 0:
            return 0
        result_dict = data[0]
        return result_dict.get('users_count')

    def get_all(self) -> List[UserDTO]:
        raise NotImplementedError

    def clear(self):
        self._context.callproc('clear_users', [])

    def add(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        self._context.callproc('add_user_soft', [params['nickname'],
                               params['email'], params['about'], params['fullname']])
        return params

    def add_many(self, entities: List[UserDTO]):
        raise NotImplementedError

    def update(self, entity: UserDTO) -> Optional[UserDTO]:

        params = [p for p in [entity.nickname, entity.email, entity.about, entity.fullname] if p is not None]
        data = None

        if entity.email is not None and entity.about is not None and entity.fullname is not None:
            data = self._context.callproc('update_user', params)

        elif entity.email is not None and entity.about is None and entity.fullname is None:
            data = self._context.callproc('update_user_by_email', params)

        elif entity.email is None and entity.about is not None and entity.fullname is None:
            data = self._context.callproc('update_user_by_about', params)

        elif entity.email is None and entity.about is None and entity.fullname is not None:
            data = self._context.callproc('update_user_by_fullname', params)

        elif entity.email is None and entity.about is not None and entity.fullname is not None:
            data = self._context.callproc('update_user_by_about_fullname', params)

        elif entity.email is not None and entity.about is None and entity.fullname is not None:
            data = self._context.callproc('update_user_by_email_fullname', params)

        elif entity.email is not None and entity.about is not None and entity.fullname is None:
            data = self._context.callproc('update_user_by_email_about', params)

        elif entity.email is None and entity.about is None and entity.fullname is None:
            data = self._context.callproc('update_user_by_empty_data', params)

        return create_one(UserDTO, data)

    def delete(self, uid: int) -> None:
        raise NotImplementedError
