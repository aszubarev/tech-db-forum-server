from sqlutils import Entity


class SrvDTO(Entity):

    @property
    def _key_field(self) -> str:
        return 'srv_id'

    def __init__(self, uid: int = None) -> None:
        super().__init__(uid)
