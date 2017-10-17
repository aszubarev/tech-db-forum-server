import logging

from flask import Blueprint, abort, request, Response, json
from injector import inject, singleton

from apiutils import BaseBlueprint

from tech_forum_api.serializers.user_serializer import UserSerializer
from tech_forum_api.services.user_service import UserService
from sqlutils import ForeignKeyViolationError, NoDataFoundError, UniqueViolationError
logging.basicConfig(level=logging.INFO)


@singleton
class UserBlueprint(BaseBlueprint[UserService]):

    @inject
    def __init__(self, service: UserService) -> None:
        super().__init__(service)

    @property
    def _name(self) -> str:
        return 'users'

    @property
    def _serializer(self) -> UserSerializer:
        return UserSerializer()

    @property
    def __service(self) -> UserService:
        return self._service

    def _create_blueprint(self) -> Blueprint:
        blueprint = Blueprint(self._name, __name__)

        @blueprint.route('/<uid>', methods=['GET'])
        def _get_by_id(uid: str):
            logging.info(uid)
            return self._get_by_id(int(uid))

        @blueprint.route('/<nickname>/create', methods=['POST'])
        def _add(nickname: str):
            try:
                return self._add(nickname=nickname)

            except UniqueViolationError:
                data = self.__service.get_by_nickname_or_email(nickname=nickname, email=request.json['email'])
                return self._return_many(data, status=409)

        @blueprint.route('/<nickname>/profile', methods=['GET'])
        def profile(nickname: str):
            try:
                user = self.__service.get_by_nickname(nickname=nickname)

                if not user:
                    logging.exception(f"Can't find user with nickname {nickname};")
                    return self._return_error(f"Can't find user with nickname {nickname}", 404)

                return self._return_one(user)

            except NoDataFoundError:
                logging.exception(f"Can't find user with nickname {nickname}")
                return self._return_error(f"Can't find user with nickname {nickname}", 404)

        @blueprint.route('/<nickname>/profile', methods=['POST'])
        def _update(nickname: str):
            try:

                return self._update(nickname=nickname)

            except NoDataFoundError:
                logging.info(f"Can't find user with nickname {nickname}")
                return self._return_error(f"Can't find user with nickname {nickname}", 404)

            except UniqueViolationError:
                logging.info(f"Can't update user with nickname {nickname}; Bad request body")
                return self._return_error(f"Can't update user with nickname {nickname};  Bad request body", 409)

        return blueprint
