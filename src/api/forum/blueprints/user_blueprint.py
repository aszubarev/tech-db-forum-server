
from flask import Blueprint, abort, request, Response, json
from injector import inject, singleton

from apiutils import BaseBlueprint

from forum.serializers.user_serializer import UserSerializer
from forum.services.forum_service import ForumService
from forum.services.user_service import UserService
from sqlutils import NoDataFoundError, UniqueViolationError


@singleton
class UserBlueprint(BaseBlueprint[UserService]):

    @inject
    def __init__(self, service: UserService, serializer: UserSerializer,
                 forum_service: ForumService) -> None:
        super().__init__(service)
        self._forumService = forum_service
        self.__serializer = serializer

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

        @blueprint.route('user/<uid>', methods=['GET'])
        def _get_by_id(uid: str):
            return self._get_by_id(int(uid))

        @blueprint.route('user/<nickname>/create', methods=['POST'])
        def _add(nickname: str):
            try:
                return self._add(nickname=nickname)

            except UniqueViolationError:
                data = self.__service.get_by_nickname_or_email(nickname=nickname, email=request.json['email'])
                return self._return_many(data, status=409)

        @blueprint.route('user/<nickname>/profile', methods=['GET'])
        def profile(nickname: str):
            try:
                user = self.__service.get_by_nickname(nickname=nickname)

                if not user:
                    return self._return_error(f"Can't find user with nickname {nickname}", 404)

                return self._return_one(user)

            except NoDataFoundError:
                return self._return_error(f"Can't find user with nickname {nickname}", 404)

        @blueprint.route('user/<nickname>/profile', methods=['POST'])
        def _update(nickname: str):
            try:

                return self._update(nickname=nickname)

            except NoDataFoundError as exp:
                return self._return_error(f"Can't update user with nickname {nickname}", 404)

            except UniqueViolationError as exp:
                return self._return_error(f"Can't update user with nickname {nickname};  Bad request", 409)

        @blueprint.route('forum/<forum_slug>/users', methods=['GET'])
        def _get_users_for_forum(forum_slug: str):
            try:

                forum = self._forumService.get_by_slug_setup(forum_slug)
                if not forum:
                    return self._return_error(f"Can't find forum: forum_slug =  {forum_slug}", 404)

                models = self._service.get_for_forum(forum.uid)
                return self._return_many(models, status=200)

            except NoDataFoundError as exp:
                return self._return_error(f"Can't find users for forum: forum_slug =  {forum_slug}", 404)

        return blueprint
