from functools import reduce
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

    @cache.memoize(600)
    def get_by_id(self, uid: int) -> Optional[Vote]:
        return super().get_by_id(uid)

    @cache.memoize(600)
    def get_for_thread(self, thread_id: int) -> List[Vote]:
        entities = self.__repo.get_for_thread(thread_id)
        return self._convert_many(entities)

    @cache.memoize(600)
    def count_for_thread(self, thread_id: int):
        """
        :param thread_id:
        :return number of all voices for thread:
        """
        models = self.get_for_thread(thread_id=thread_id)
        return len(models)  # return number of all models

    @cache.memoize(600)
    def votes(self, thread_id: int) -> int:
        """
        :param thread_id:
        :return sum of all voices for thread:
        """
        models = self.get_for_thread(thread_id=thread_id)
        votes = reduce(lambda a, vote: a + vote.value, models, 0)
        return votes

    @property
    def __repo(self) -> VoteRepository:
        return self._repo

    def _convert(self, entity: VoteDTO) -> Optional[Vote]:
        if not entity:
            return None

        return self._converter.convert(entity)

    @staticmethod
    def _clear_cache() -> None:
        # TODO don't remember update cache
        cache.delete_memoized(VoteService.get_by_id)
        cache.delete_memoized(VoteService.get_for_thread)
        cache.delete_memoized(VoteService.count_for_thread)
        cache.delete_memoized(VoteService.votes)

