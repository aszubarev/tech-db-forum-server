from sqlutils import Entity


class ForumDTO(Entity):

    @property
    def _key_field(self) -> str:
        return 'forum_id'

    def __init__(self, uid: int = None,
                 slug: str = None,
                 user_id: int = None,
                 title: str = None) -> None:
        super().__init__(uid)

        self._slug = slug
        self._user_id = user_id
        self._title = title

    @property
    def slug(self) -> str:
        return self._slug

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def title(self) -> str:
        return self._title
