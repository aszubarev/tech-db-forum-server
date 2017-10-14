from datetime import datetime

from sqlutils import Model
from tech_forum_api.models.forum import Forum
from tech_forum_api.models.user import User


class Thread(Model):

    def __init__(self, uid: int) -> None:
        super().__init__(uid)

        self._slug: str = None
        self._forum: Forum = None
        self._user: User = None
        self._created: datetime = None
        self._message: str = None
        self._title: str = None

    @property
    def slug(self) -> str:
        return self._slug

    @property
    def forum(self) -> Forum:
        return self._forum

    @property
    def user(self) -> User:
        return self._user

    @property
    def created(self) -> datetime:
        return self._created

    @property
    def message(self) -> str:
        return self._message

    @property
    def title(self) -> str:
        return self._title

    def fill(self, slug: str, forum: Forum, user: User, created: datetime, message: str, title: str) -> "Thread":
        self._slug = slug
        self._forum = forum
        self._user = user
        self._created = created
        self._message = message
        self._title = title
        self._filled()
        return self
