from datetime import datetime

from sqlutils import Entity


class ThreadDTO(Entity):

    @property
    def _key_field(self) -> str:
        return 'thread_id'

    def __init__(self, uid: int = None,
                 slug: str = None,
                 forum_id: int = None,
                 forum_slug: str = None,
                 user_id: int = None,
                 user_nickname: str = None,
                 created: datetime = None,
                 message: str = None,
                 title: str = None) -> None:
        super().__init__(uid)

        self._slug = slug
        self._forum_id = forum_id
        self._forum_slug = forum_slug
        self._user_id = user_id
        self._user_nickname = user_nickname
        self._created = created
        self._message = message
        self._title = title

    @property
    def slug(self) -> str:
        return self._slug

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
    def created(self) -> datetime:
        return self._created

    @property
    def message(self) -> str:
        return self._message

    @property
    def title(self) -> str:
        return self._title

    @user_nickname.setter
    def user_nickname(self, value):
        self._user_nickname = value

    @forum_slug.setter
    def forum_slug(self, value):
        self._forum_slug = value
