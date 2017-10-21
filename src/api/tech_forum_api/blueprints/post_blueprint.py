import logging

from flask import Blueprint, abort, request, Response, json
from injector import inject, singleton

from apiutils import BaseBlueprint
from apiutils.errors.bad_request_error import BadRequestError

from tech_forum_api.serializers.post_serializer import PostSerializer
from sqlutils import NoDataFoundError, UniqueViolationError
from tech_forum_api.serializers.post_serializer_detail import PostSerializerFull
from tech_forum_api.services.post_service import PostService

logging.basicConfig(level=logging.INFO)


@singleton
class PostBlueprint(BaseBlueprint[PostService]):

    @inject
    def __init__(self, service: PostService, serializer: PostSerializer,
                 post_serializer_full: PostSerializerFull) -> None:
        super().__init__(service)
        self.__serializer = serializer
        self._postSerializerFull = post_serializer_full

    @property
    def _name(self) -> str:
        return 'posts'

    @property
    def _serializer(self) -> PostSerializer:
        return self.__serializer

    @property
    def __service(self) -> PostService:
        return self._service

    def _create_blueprint(self) -> Blueprint:
        blueprint = Blueprint(self._name, __name__)

        @blueprint.route('thread/<slug_or_id>/create', methods=['POST'])
        def _add_many(slug_or_id: str):
            try:
                return self._add_many(thread_slug_or_id=slug_or_id)

            except NoDataFoundError as exp:
                logging.error(exp, exc_info=True)
                return self._return_error(f"Can't find thread by slag = {slug_or_id}", 404)

            except UniqueViolationError as exp:
                logging.error(exp, exc_info=True)
                return self._return_error(f"Can't create thread by slag = {slug_or_id}", 409)

        @blueprint.route('thread/<slug_or_id>/posts', methods=['GET'])
        def _posts(slug_or_id: str):
            try:

                models = self.__service.get_posts_for_thread(slug_or_id)
                return self._return_many(models, status=200)

            except NoDataFoundError as exp:
                logging.error(exp, exc_info=True)
                return self._return_error(f"Can't get thread by forum slug_or_id = {slug_or_id}", 404)

            except BadRequestError as exp:
                logging.error(exp, exc_info=True)
                return self._return_error(f"Bad request", 400)

        @blueprint.route('post/<uid>/details', methods=['GET'])
        def _details(uid: int):
            model = self.__service.get_by_id(uid)

            if not model:
                return self._retunr_error(f"Can't find post by id = {uid}", 404)

            response = self._postSerializerFull.dump(model)
            return Response(response=json.dumps(response), status=200, mimetype='application/json')

        @blueprint.route('post/<uid>/details', methods=['POST'])
        def _update(uid: int):
            model = self.__service.get_by_id(uid)

            if not model:
                return self._retunr_error(f"Can't find post by uid = {uid}", 404)

            return self._update(id=uid, message=request.json.get('message'))

        return blueprint
