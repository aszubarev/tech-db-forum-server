import logging
from flask import Blueprint, request, Response, json
from injector import inject, singleton

from forum.persistence.repositories.forum_repository import ForumRepository
from forum.persistence.repositories.user_repository import UserRepository
from sqlutils import UniqueViolationError

from apiutils import BaseBlueprint


@singleton
class UserBlueprint(BaseBlueprint[UserRepository]):

    @inject
    def __init__(self, repo: UserRepository, forum_repo: ForumRepository) -> None:
        super().__init__(repo)
        self._forumRepo = forum_repo

    @property
    def _name(self) -> str:
        return 'users'

    @property
    def __repo(self) -> UserRepository:
        return self._repo

    def _create_blueprint(self) -> Blueprint:

        blueprint = Blueprint(self._name, __name__)

        @blueprint.route('user/<nickname>/create', methods=['POST'])
        def _add(nickname: str):
            try:

                params = request.json
                params.update({
                    'nickname': nickname
                })
                response = self.__repo.add(params)
                return Response(response=json.dumps(response), status=201, mimetype='application/json')

            except UniqueViolationError:
                response = self.__repo.get_by_nickname_or_email(nickname=nickname, email=request.json['email'])
                return Response(response=json.dumps(response), status=409, mimetype='application/json')

        @blueprint.route('user/<nickname>/profile', methods=['GET'])
        def profile(nickname: str):
            data = self.__repo.get_by_nickname(nickname=nickname)
            if not data:
                return self._return_error(f"Can't find user with nickname {nickname}", 404)

            return Response(response=json.dumps(data), status=200, mimetype='application/json')

        @blueprint.route('user/<nickname>/profile', methods=['POST'])
        def _update(nickname: str):
            try:

                # TODO use light version
                user = self.__repo.get_by_nickname(nickname=nickname)
                if not user:
                    return self._return_error(f"Can't update user with nickname {nickname}", 404)

                # TODO update by uid, not not nickname
                params = request.json
                params.update({
                    'nickname': user['nickname']
                })
                data = self.__repo.update(params)
                return Response(response=json.dumps(data), status=200, mimetype='application/json')

            except UniqueViolationError:
                return self._return_error(f"Can't update user with nickname {nickname};", 409)

        @blueprint.route('forum/<forum_slug>/users', methods=['GET'])
        def _get_users_for_forum(forum_slug: str):

            forum = self._forumRepo.get_by_slug(forum_slug)
            if not forum:
                return self._return_error(f"Can't find forum: forum_slug =  {forum_slug}", 404)

            desc = request.args.get('desc')
            limit = request.args.get('limit')
            since = request.args.get('since')

            data = self.__repo.get_for_forum(forum_id=forum['forum_id'], since=since, limit=limit, desc=desc)
            return Response(response=json.dumps(data), status=200, mimetype='application/json')

        return blueprint
