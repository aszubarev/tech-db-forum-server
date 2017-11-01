import logging

from flask import Blueprint, request, Response, json
from injector import inject, singleton

from apiutils import BaseBlueprint

from forum.serializers.forum_serializer import ForumSerializer
from forum.serializers.thread_serializer import ThreadSerializer
from forum.services.forum_service import ForumService
from forum.services.user_service import UserService
from sqlutils import NoDataFoundError, UniqueViolationError
from forum.services.thread_service import ThreadService


@singleton
class ForumBlueprint(BaseBlueprint[ForumService]):

    @inject
    def __init__(self, service: ForumService, serializer: ForumSerializer, user_service: UserService,
                 thread_service: ThreadService, thread_serializer: ThreadSerializer) -> None:
        super().__init__(service)
        self.__serializer = serializer

        self._thread_service = thread_service
        self._thread_serializer = thread_serializer

        self._userService = user_service

    @property
    def _name(self) -> str:
        return 'forums'

    @property
    def _serializer(self) -> ForumSerializer:
        return self.__serializer

    @property
    def __service(self) -> ForumService:
        return self._service

    def _create_blueprint(self) -> Blueprint:
        blueprint = Blueprint(self._name, __name__)

        @blueprint.route('forum/create', methods=['POST'])
        def _add():
            try:
                user = self._userService.get_by_nickname_soft(request.json['user'])
                if not user:
                    return self._return_error(f"Can't find user with nickname {request.json['user']}", 404)

                data = self._service.add_soft(body=request.json,
                                              user_id=user['user_id'], user_nickname=user['nickname'])
                return Response(response=json.dumps(data), status=201, mimetype='application/json')

            except UniqueViolationError:
                data = self.__service.get_by_slug_soft(request.json['slug'])
                return Response(response=json.dumps(data), status=409, mimetype='application/json')

        @blueprint.route('forum/<slug>/details', methods=['GET'])
        def _details(slug: str):
            data = self.__service.get_by_slug_soft(slug)
            if not data:
                return self._return_error(f"Can't find forum details by slag = {slug}", 404)

            return Response(response=json.dumps(data), status=200, mimetype='application/json')

        return blueprint
