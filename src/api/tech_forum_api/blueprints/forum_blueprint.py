import logging

from flask import Blueprint, abort, request, Response, json
from injector import inject, singleton

from apiutils import BaseBlueprint

from tech_forum_api.serializers.forum_serializer import ForumSerializer
from tech_forum_api.services.forum_service import ForumService
from sqlutils import NoDataFoundError, UniqueViolationError
logging.basicConfig(level=logging.INFO)


@singleton
class ForumBlueprint(BaseBlueprint[ForumService]):

    @inject
    def __init__(self, service: ForumService, serializer: ForumSerializer) -> None:
        super().__init__(service)
        self.__serializer = serializer

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

        @blueprint.route('/<uid>', methods=['GET'])
        def _get_by_id(uid: str):
            logging.exception(uid)
            return self._get_by_id(int(uid))

        @blueprint.route('/create', methods=['POST'])
        def _add():
            try:
                data = {}
                return self._add(data)

            except UniqueViolationError:
                forum = self.__service.get_by_slug(request.json['slug'])
                return self._return_one_with_status(forum, 409)

            except NoDataFoundError:
                return self._return_error(f"Can't find user with nickname {request.json['user']}", 404)

        return blueprint
