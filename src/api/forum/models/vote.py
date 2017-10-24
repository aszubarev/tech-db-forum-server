from sqlutils import Model
from forum.models.thread import Thread
from forum.models.user import User


class Vote(Model):

    def __init__(self, uid: int) -> None:
        super().__init__(uid)

        self._user: User = None
        self._thread: Thread = None
        self._value: int = None

    @property
    def user(self) -> User:
        return self._user

    @property
    def thread(self) -> Thread:
        return self._thread

    @property
    def value(self) -> int:
        return self._value

    def fill(self, user: User, thread: Thread, vote_value: int) -> "Vote":
        self._user = user
        self._thread = thread
        self._value = vote_value
        self._filled()
        return self
