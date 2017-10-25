from sqlutils import Entity


class ForumDTO(Entity):

    @property
    def _key_field(self) -> str:
        return 'forum_id'

    def __init__(self, uid: int = None,
                 slug: str = None,
                 user_id: int = None,
                 user_nickname: str = None,
                 title: str = None,
                 threads: int = None,
                 posts: int = None) -> None:
        super().__init__(uid)

        self._slug = slug
        self._user_id = user_id
        self._user_nickname = user_nickname
        self._title = title
        self._threads = threads
        self._posts = posts

    @property
    def slug(self) -> str:
        return self._slug

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def user_nickname(self) -> str:
        return self._user_nickname

    @property
    def title(self) -> str:
        return self._title

    @property
    def threads(self) -> int:
        return self._threads

    @property
    def posts(self) -> int:
        return self._posts

    @user_nickname.setter
    def user_nickname(self, value):
        self._user_nickname = value
