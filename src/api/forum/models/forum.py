from sqlutils import Model
from forum.models.user import User


class Forum(Model):

    def __init__(self, uid: int) -> None:
        super().__init__(uid)

        self._slug: str = None
        self._user: User = None
        self._title: str = None
        self._threads: int = None
        self._posts: int = None

    @property
    def slug(self) -> str:
        return self._slug

    @property
    def user(self) -> User:
        return self._user

    @property
    def title(self) -> str:
        return self._title
    
    @property
    def threads(self) -> int:
        return self._threads
    
    @property
    def posts(self) -> int:
        return self._posts

    def fill(self, slug: str = None, user: User = None,
             title: str = None, threads: int = None, posts: int = None) -> "Forum":
        self._slug = slug
        self._user = user
        self._title = title
        self._threads = threads
        self._posts = posts
        self._filled()
        return self
