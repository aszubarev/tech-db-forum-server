from datetime import datetime

from sqlutils import Entity


class ThreadDTO(Entity):

    @property
    def _key_field(self) -> str:
        return 'thread_id'

    def __init__(self, uid: int = None,
                 slug: str = None,
                 forum_id: int = None,
                 user_id: int = None,
                 created: datetime = None,
                 message: str = None,
                 title: str = None) -> None:
        super().__init__(uid)

        self._slug = slug
        self._forum_id = forum_id
        self._user_id = user_id
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
    def user_id(self) -> int:
        return self._user_id

    @property
    def created(self) -> datetime:
        return self._created

    @property
    def message(self) -> str:
        return self._message

    @property
    def title(self) -> str:
        return self._title
