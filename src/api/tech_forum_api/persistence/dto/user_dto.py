from sqlutils import Entity


class UserDTO(Entity):

    @property
    def _key_field(self) -> str:
        return 'actor_id'

    def __init__(self, uid: int = None,
                 nickname: str = None,
                 email: str = None,
                 about: str = None,
                 fullname: str = None) -> None:
        super().__init__(uid)

        self._nickname = nickname
        self._email = email
        self._about = about
        self._fullname = fullname

    @property
    def nickname(self) -> str:
        return self._nickname

    @property
    def email(self) -> str:
        return self._email

    @property
    def about(self) -> str:
        return self._about

    @property
    def about(self) -> str:
        return self._fullname
