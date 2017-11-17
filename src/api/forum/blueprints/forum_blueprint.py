import logging

from flask import Blueprint, request, Response, json
from injector import inject, singleton

from apiutils import BaseBlueprint
from forum.persistence.repositories.forum_repository import ForumRepository
from forum.persistence.repositories.user_repository import UserRepository

from sqlutils import UniqueViolationError
import ujson

@singleton
class ForumBlueprint(BaseBlueprint[ForumRepository]):

    @inject
    def __init__(self, repo: ForumRepository, user_repo: UserRepository) -> None:
        super().__init__(repo)
        self._userRepo = user_repo

    @property
    def _name(self) -> str:
        return 'forums'

    @property
    def __repo(self) -> ForumRepository:
        return self._repo

    def _create_blueprint(self) -> Blueprint:
        blueprint = Blueprint(self._name, __name__)

        @blueprint.route('forum/create', methods=['POST'])
        def _add():
            body = ujson.loads(request.data)
            # body = request.json
            try:
                user = self._userRepo.get_by_nickname(body['user'])
                if not user:
                    return self._return_error(f"Can't find user with nickname {body['user']}", 404)

                params = body
                params.update({
                    'user_id': user['user_id'],
                    'user': user['nickname']
                })
                data = self.__repo.add(params)
                return Response(response=ujson.dumps(data), status=201, mimetype='application/json')

            except UniqueViolationError:
                data = self.__repo.get_by_slug(body['slug'])
                return Response(response=ujson.dumps(data), status=409, mimetype='application/json')

        @blueprint.route('forum/<slug>/details', methods=['GET'])
        def _details(slug: str):
            data = self.__repo.get_by_slug(slug)
            if not data:
                return self._return_error(f"Can't find forum details by slag = {slug}", 404)

            return Response(response=ujson.dumps(data), status=200, mimetype='application/json')

        return blueprint
