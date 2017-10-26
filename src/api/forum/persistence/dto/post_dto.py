from datetime import datetime
from typing import List

from sqlutils import Entity


class PostDTO(Entity):

    @property
    def _key_field(self) -> str:
        return 'post_id'

    def __init__(self, uid: int = None,
                 thread_id: int = None,
                 forum_id: int = None,
                 forum_slug: str = None,
                 user_id: int = None,
                 user_nickname: str = None,
                 parent_id: int = None,
                 message: str = None,
                 created: datetime = None,
                 is_edited: bool = None,
                 path: List[int] = None) -> None:
        super().__init__(uid)

        self._thread_id = thread_id
        self._forum_id = forum_id
        self._forum_slug = forum_slug
        self._user_id = user_id
        self._user_nickname = user_nickname
        self._parent_id = parent_id
        self._message = message
        self._created = created
        self._is_edited = is_edited
        self._path = path

    @property
    def thread_id(self) -> int:
        return self._thread_id

    @property
    def forum_id(self) -> int:
        return self._forum_id

    @property
    def forum_slug(self) -> str:
        return self._forum_slug

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def user_nickname(self) -> str:
        return self._user_nickname

    @property
    def parent_id(self) -> int:
        return self._parent_id

    @property
    def message(self) -> str:
        return self._message

    @property
    def created(self) -> datetime:
        return self._created

    @property
    def is_edited(self) -> bool:
        return self._is_edited

    @property
    def path(self) -> List[int]:
        return self._path

    @path.setter
    def path(self, value):
        self._path = value
