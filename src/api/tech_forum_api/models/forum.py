from sqlutils import Model
from tech_forum_api.models.user import User


class Forum(Model):

    def __init__(self, uid: int) -> None:
        super().__init__(uid)

        self._slug: str = None
        self._user: User = None
        self._title: str = None

    @property
    def slug(self) -> str:
        return self._slug

    @property
    def user(self) -> User:
        return self._user

    @property
    def title(self) -> str:
        return self._title

    def fill(self, slug: str, user: User, title: str) -> "Forum":
        self._slug = slug
        self._user = user
        self._title = title
        self._filled()
        return self
