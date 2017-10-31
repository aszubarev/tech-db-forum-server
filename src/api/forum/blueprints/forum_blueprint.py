
from flask import Blueprint, request, Response, json
from injector import inject, singleton

from apiutils import BaseBlueprint

from forum.serializers.forum_serializer import ForumSerializer
from forum.serializers.thread_serializer import ThreadSerializer
from forum.services.forum_service import ForumService
from sqlutils import NoDataFoundError, UniqueViolationError
from forum.services.thread_service import ThreadService


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
            model = self._service.get_by_slug(slug)
            if not model:
                return self._return_error(f"Can't find forum details by slag = {slug}", 404)
            return self._return_one(model, status=200)

        return blueprint
