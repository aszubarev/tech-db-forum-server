from sqlutils import Model


class User(Model):

    def __init__(self, uid: int) -> None:
        super().__init__(uid)

        self._nickname: str = None
        self._email: str = None
        self._about: str = None
        self._fullname: str = None

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
    def fullname(self) -> str:
        return self._fullname

    def fill(self, nickname: str, email: str, about: str, fullname: str) -> "User":
        self._nickname = nickname
        self._email = email
        self._about = about
        self._fullname = fullname
        self._filled()
        return self
