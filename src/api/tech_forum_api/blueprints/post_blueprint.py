import logging

from flask import Blueprint, abort, request, Response, json
from injector import inject, singleton

from apiutils import BaseBlueprint

from tech_forum_api.serializers.post_serializer import PostSerializer
from sqlutils import NoDataFoundError, UniqueViolationError
from tech_forum_api.services.post_service import PostService

logging.basicConfig(level=logging.INFO)


@singleton
class PostBlueprint(BaseBlueprint[PostService]):

    @inject
    def __init__(self, service: PostService, serializer: PostSerializer) -> None:
        super().__init__(service)
        self.__serializer = serializer

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

            except NoDataFoundError:
                return self._return_error(f"Can't find thread by slag = {slug_or_id}", 404)

            except UniqueViolationError:
                return self._return_error(f"Can't create thread by slag = {slug_or_id}", 409)

        return blueprint
