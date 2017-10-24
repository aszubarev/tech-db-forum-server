from sqlutils import Entity


class VoteDTO(Entity):

    @property
    def _key_field(self) -> str:
        return 'vote_id'

    def __init__(self, uid: int = None,
                 user_id: int = None,
                 thread_id: int = None,
                 vote_value: int = None) -> None:
        super().__init__(uid)

        self._user_id = user_id
        self._thread_id = thread_id
        self._vote_value = vote_value

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def thread_id(self) -> int:
        return self._thread_id

    @property
    def vote_value(self) -> int:
        return self._vote_value
