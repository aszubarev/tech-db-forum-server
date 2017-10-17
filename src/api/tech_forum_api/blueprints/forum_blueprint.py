import logging

from flask import Blueprint, abort, request, Response, json
from injector import inject, singleton

from apiutils import BaseBlueprint

from tech_forum_api.serializers.forum_serializer import ForumSerializer
from tech_forum_api.serializers.thread_serializer import ThreadSerializer
from tech_forum_api.services.forum_service import ForumService
from sqlutils import NoDataFoundError, UniqueViolationError
from tech_forum_api.services.thread_service import ThreadService

logging.basicConfig(level=logging.INFO)


@singleton
class ForumBlueprint(BaseBlueprint[ForumService]):

    @inject
    def __init__(self, service: ForumService, serializer: ForumSerializer,
                 thread_service: ThreadService, thread_serializer: ThreadSerializer) -> None:
        super().__init__(service)
        self.__serializer = serializer

        self._thread_service = thread_service
        self._thread_serializer = thread_serializer

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

        @blueprint.route('forum/<uid>', methods=['GET'])
        def _get_by_id(uid: str):
            logging.exception(uid)
            return self._get_by_id(int(uid))

        @blueprint.route('forum/create', methods=['POST'])
        def _add():
            try:
                return self._add()

            except UniqueViolationError:
                forum = self.__service.get_by_slug(request.json['slug'])
                return self._return_one(forum, status=409)

            except NoDataFoundError:
                return self._return_error(f"Can't find user with nickname {request.json['user']}", 404)

        @blueprint.route('forum/<slug>/details', methods=['GET'])
        def _details(slug: str):
            try:
                model = self._service.get_by_slug(slug)
                return self._return_one(model, status=200)
            except NoDataFoundError:
                return self._return_error(f"Can't find forum details by slag = {slug}", 404)

        return blueprint
