import logging

from flask import Blueprint, abort, request, Response, json
from injector import inject, singleton

from apiutils import BaseBlueprint

from tech_forum_api.serializers.thread_serializer import ThreadSerializer
from sqlutils import NoDataFoundError, UniqueViolationError
from tech_forum_api.services.thread_service import ThreadService

logging.basicConfig(level=logging.INFO)


@singleton
class ThreadBlueprint(BaseBlueprint[ThreadService]):

    @inject
    def __init__(self, service: ThreadService, serializer: ThreadSerializer) -> None:
        super().__init__(service)
        self.__serializer = serializer

    @property
    def _name(self) -> str:
        return 'threads'

    @property
    def _serializer(self) -> ThreadSerializer:
        return self.__serializer

    @property
    def __service(self) -> ThreadService:
        return self._service

    def _create_blueprint(self) -> Blueprint:
        blueprint = Blueprint(self._name, __name__)

        @blueprint.route('forum/<slug>/create', methods=['POST'])
        def _add(slug: str):
            try:
                logging.info(f"[ThreadBlueprint._add] Try add thread by slug = {slug}")
                response = self._add({'forum': slug})
                logging.info(f"[ThreadBlueprint._add] Complete add thread by slug = {slug}")
                return response

            except NoDataFoundError:
                return self._return_error(f"Can't create thread by slag = {slug}", 404)

            except UniqueViolationError:
                logging.info(f"[ThreadBlueprint._add] Try Handle UniqueViolationError")
                thread_slug = request.json['slug']
                model = self._service.get_by_slug(thread_slug)
                response = self._return_one(model, status=409)
                logging.info(f"[ThreadBlueprint._add] Complete Handle UniqueViolationError")
                return response

        @blueprint.route('forum/<slug>/threads', methods=['GET'])
        def _get_threads_by_forum(slug: str):
            try:
                models = self.__service.get_for_forum(slug)
                return self._return_many(models, status=200)

            except NoDataFoundError:
                return self._return_error(f"Can't get threads by forum slag = {slug}", 404)

        return blueprint
