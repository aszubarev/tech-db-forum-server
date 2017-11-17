
from flask import Blueprint, Response, json
from injector import inject, singleton

from apiutils import BaseBlueprint
from forum.persistence.repositories.forum_repository import ForumRepository
from forum.persistence.repositories.post_repository import PostRepository
from forum.persistence.repositories.service_repository import SrvRepository
from forum.persistence.repositories.thread_repository import ThreadRepository
from forum.persistence.repositories.user_repository import UserRepository
from forum.persistence.repositories.vote_repositpry import VoteRepository
import ujson


@singleton
class SrvBlueprint(BaseBlueprint[SrvRepository]):

    @inject
    def __init__(self, repo: SrvRepository, forum_repo: ForumRepository, thread_repo: ThreadRepository,
                 post_repo: PostRepository, user_repo: UserRepository, vote_repo: VoteRepository) -> None:

        super().__init__(repo)
        self._forumRepo = forum_repo
        self._threadRepo = thread_repo
        self._postService = post_repo
        self._userRepo = user_repo
        self._voteRepo = vote_repo

    @property
    def _name(self) -> str:
        return 'service'

    @property
    def __repo(self) -> SrvRepository:
        return self._repo

    def _create_blueprint(self) -> Blueprint:
        blueprint = Blueprint(self._name, __name__)

        @blueprint.route('service/status', methods=['GET'])
        def _status():

            response = {
                'forum': self._forumRepo.get_count(),
                'thread': self._threadRepo.get_count(),
                'post': self._postService.get_count(),
                'user': self._userRepo.get_count()
            }

            return Response(response=ujson.dumps(response), status=200, mimetype='application/json')

        @blueprint.route('service/clear', methods=['POST'])
        def _clear():
            self._userRepo.clear()
            self._forumRepo.clear()
            self._threadRepo.clear()
            self._postService.clear()
            self._voteRepo.clear()
            return Response(response="Complete clear", status=200, mimetype='application/json')

        return blueprint
