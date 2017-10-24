from sqlutils import Model


class Srv(Model):

    def __init__(self, uid: int) -> None:
        super().__init__(uid)

        self._forums: int = None
        self._threads: int = None
        self._posts: int = None
        self._users: int = None

    @property
    def forums(self) -> int:
        return self._forums

    @property
    def threads(self) -> int:
        return self._threads

    @property
    def posts(self) -> int:
        return self._posts

    @property
    def users(self) -> int:
        return self._users

    def fill(self, forums: int, threads: int, posts: int, users: int) -> "Srv":
        self._forums = forums
        self._threads = threads
        self._posts = posts
        self._users = users
        self._filled()
        return self
