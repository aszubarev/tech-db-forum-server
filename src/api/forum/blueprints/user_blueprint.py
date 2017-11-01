import logging
from flask import Blueprint, abort, request, Response, json, jsonify
from injector import inject, singleton

from apiutils import BaseBlueprint
from forum.serializers.soft.user_serializer_soft import UserSerializerSoft

from forum.serializers.user_serializer import UserSerializer
from forum.services.forum_service import ForumService
from forum.services.user_service import UserService
from sqlutils import NoDataFoundError, UniqueViolationError


@singleton
class UserBlueprint(BaseBlueprint[UserService]):

    @inject
    def __init__(self, service: UserService, serializer: UserSerializer,
                 user_serializer_soft: UserSerializerSoft, forum_service: ForumService) -> None:
        super().__init__(service)
        self._forumService = forum_service
        self.__serializer = serializer
        self._userSerializerSoft = user_serializer_soft

    @property
    def _name(self) -> str:
        return 'users'

    @property
    def _serializer(self) -> UserSerializer:
        return  self.__serializer

    @property
    def __service(self) -> UserService:
        return self._service

    def _create_blueprint(self) -> Blueprint:
        blueprint = Blueprint(self._name, __name__)

        @blueprint.route('user/<nickname>/create', methods=['POST'])
        def _add(nickname: str):
            try:

                data = self.__service.add_soft(body=request.json, nickname=nickname)
                response = self._userSerializerSoft.dump(data)
                return Response(response=json.dumps(response), status=201, mimetype='application/json')

            except UniqueViolationError:
                data = self.__service.get_by_nickname_or_email(nickname=nickname, email=request.json['email'])
                return Response(response=json.dumps(data), status=409, mimetype='application/json')

        @blueprint.route('user/<nickname>/profile', methods=['GET'])
        def profile(nickname: str):
            try:
                data = self.__service.get_by_nickname_soft(nickname=nickname)
                if not data:
                    return self._return_error(f"Can't find user with nickname {nickname}", 404)

                return Response(response=json.dumps(data), status=200, mimetype='application/json')

            except NoDataFoundError:
                return self._return_error(f"Can't find user with nickname {nickname}", 404)

        @blueprint.route('user/<nickname>/profile', methods=['POST'])
        def _update(nickname: str):
            try:

                # TODO use light version
                user = self.__service.get_by_nickname_soft(nickname=nickname)
                if not user:
                    return self._return_error(f"Can't update user with nickname {nickname}", 404)

                # TODO update by uid, not not nickname
                data = self.__service.update_soft(body=request.json, nickname=user['nickname'])
                return Response(response=json.dumps(data), status=200, mimetype='application/json')

            except NoDataFoundError as exp:
                return self._return_error(f"Can't update user with nickname {nickname}", 404)

            except UniqueViolationError as exp:
                return self._return_error(f"Can't update user with nickname {nickname};  Bad request", 409)

        @blueprint.route('forum/<forum_slug>/users', methods=['GET'])
        def _get_users_for_forum(forum_slug: str):

            forum = self._forumService.get_by_slug_setup(forum_slug)
            if not forum:
                return self._return_error(f"Can't find forum: forum_slug =  {forum_slug}", 404)

            data = self._service.get_for_forum(forum_id=forum.uid, args=request.args)
            return Response(response=json.dumps(data), status=200, mimetype='application/json')

        return blueprint
