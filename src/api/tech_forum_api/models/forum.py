from sqlutils import Model


class Forum(Model):

    def __init__(self, uid: int) -> None:
        super().__init__(uid)

        self._slug: str = None
        self._nickname: str = None
        self._title: str = None

    @property
    def slug(self) -> str:
        return self._slug

    @property
    def nickname(self) -> str:
        return self._nickname

    @property
    def title(self) -> str:
        return self._title

    def fill(self, slug: str, nickname: str, title: str) -> "Forum":
        self._slug = slug
        self._nickname = nickname
        self._title = title
        self._filled()
        return self
