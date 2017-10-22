import logging
from typing import Optional, List

from injector import inject
from sqlutils import DataContext, Repository

from tech_forum_api.persistence.dto.service_dto import SrvDTO


class SrvRepository(Repository[SrvDTO]):

    @inject
    def __init__(self, context: DataContext) -> None:
        self._context = context

    def get_by_id(self, uid: int) -> Optional[SrvDTO]:
        raise NotImplementedError

    def get_all(self) -> List[SrvDTO]:
        raise NotImplementedError

    def add(self, entity: SrvDTO) -> Optional[SrvDTO]:
        raise NotImplementedError

    def update(self, entity: SrvDTO) -> Optional[SrvDTO]:
        raise NotImplementedError

    def delete(self, uid: int) -> None:
        raise NotImplementedError
