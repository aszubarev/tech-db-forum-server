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

        @blueprint.route('/<slug>/create', methods=['POST'])
        def _create_thread(slug: str):
            try:

                data = {'forum': slug}
                serialized_data = request.json
                serialized_data.update(data)
                entity = self._thread_serializer.load(serialized_data)

                # return self._return_error(f"Can't create thread by slag = {slug}", 201)

                model = self._thread_service.add(entity)
                if model is None:
                    return self._return_error(f"Can't create thread by slag = {slug}", 404)
                response = self._thread_serializer.dump(model)
                return Response(response=json.dumps(response),
                                status=201, mimetype='application/json')

            except NoDataFoundError:
                return self._return_error(f"Can't create thread by slag = {slug}", 404)

            except UniqueViolationError:
                return self._return_error(f"Can't create thread by slag = {slug}", 409)

        @blueprint.route('/<slug>/details', methods=['GET'])
        def _forum_details(slug: str):
            try:
                model = self._service.get_by_slug(slug)
                return self._return_one_with_status(model, 200)
            except NoDataFoundError:
                return self._return_error(f"Can't find forum details by slag = {slug}", 404)

        return blueprint
