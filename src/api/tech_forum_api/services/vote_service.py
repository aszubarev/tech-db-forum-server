from typing import Optional, List

from injector import inject, singleton
from sqlutils import Service

from tech_forum_api.cache import cache
from tech_forum_api.converters.vote_converter import VoteConverter
from tech_forum_api.models.vote import Vote
from tech_forum_api.persistence.dto.vote_dto import VoteDTO
from tech_forum_api.persistence.repositories.vote_repositpry import VoteRepository


@singleton
class VoteService(Service[Vote, VoteDTO, VoteRepository]):

    @inject
    def __init__(self, repo: VoteRepository) -> None:
        super().__init__(repo)
        self._converter = VoteConverter()

    @property
    def __repo(self) -> VoteRepository:
        return self._repo

    def _convert(self, entity: VoteDTO) -> Optional[Vote]:
        if not entity:
            return None

        return self._converter.convert(entity)

    @staticmethod
    def _clear_cache() -> None:
        # cache.delete_memoized(VoteService.get_by_id)
        pass
        #TODO dont remember update cache
