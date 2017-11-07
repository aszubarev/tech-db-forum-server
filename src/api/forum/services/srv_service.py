from injector import inject, singleton

from sqlutils import Service

from forum.models.service import Srv
from forum.persistence.dto.service_dto import SrvDTO
from forum.persistence.repositories.service_repository import SrvRepository
from forum.services.forum_service import ForumService
from forum.services.post_service import PostRepository
from forum.services.thread_service import ThreadService
from forum.services.user_service import UserService
from forum.services.vote_service import VoteService


@singleton
class SrvService(Service[Srv, SrvDTO, SrvRepository]):

    @inject
    def __init__(self, repo: SrvRepository,
                 forum_service: ForumService,
                 thread_service: ThreadService,
                 post_service: PostRepository,
                 user_service: UserService,
                 vote_service: VoteService) -> None:
        super().__init__(repo)
        self._forumService = forum_service
        self._threadService = thread_service
        self._postService = post_service
        self._userService = user_service
        self._voteService = vote_service

    def status(self) -> Srv:
        forums = self._forumService.get_count()
        threads = self._threadService.get_count()
        posts = self._postService.get_count()
        users = self._userService.get_count()
        model = Srv(uid=None).fill(
            forums=forums,
            threads=threads,
            posts=posts,
            users=users
        )
        return model

    def clear(self) -> None:
        self._userService.clear()
        self._forumService.clear()
        self._threadService.clear()
        self._postService.clear()
        self._voteService.clear()

    def _convert(self, entity: SrvDTO):
        raise NotImplementedError

    @staticmethod
    def _clear_cache():
        raise NotImplementedError
