import logging

from flask import Blueprint, abort, request, Response, json
from injector import inject, singleton

from apiutils import BaseBlueprint
from apiutils.errors.bad_request_error import BadRequestError
from forum.serializers.user_serializer import UserSerializer

from forum.serializers.vote_serializer import VoteSerializer
from forum.serializers.thread_serializer import ThreadSerializer
from sqlutils import NoDataFoundError, UniqueViolationError
from forum.services.thread_service import ThreadService
from forum.services.user_service import UserService
from forum.services.vote_service import VoteService

logging.basicConfig(level=logging.INFO)


@singleton
class VoteBlueprint(BaseBlueprint[VoteService]):

    @inject
    def __init__(self, service: VoteService, serializer: VoteSerializer,
                 thread_service: ThreadService, thread_serializer: ThreadSerializer,
                 user_service: UserService, user_serializer: UserSerializer) -> None:
        super().__init__(service)
        self.__serializer = serializer
        self._thread_service = thread_service
        self._thread_serializer = thread_serializer
        self._user_service = user_service
        self._user_serializer = user_serializer

    @property
    def _name(self) -> str:
        return 'votes'

    @property
    def _serializer(self) -> VoteSerializer:
        return self.__serializer

    @property
    def __service(self) -> VoteService:
        return self._service

    def _create_blueprint(self) -> Blueprint:
        blueprint = Blueprint(self._name, __name__)

        @blueprint.route('thread/<slug_or_id>/vote', methods=['POST'])
        def _add(slug_or_id: str):
            try:
                return self._add(thread_slug_or_id=slug_or_id, status=200)

            except NoDataFoundError as exp:
                logging.error(exp, exc_info=True)
                return self._return_error(f"Can't create thread by request = {request.json}", 404)

            except BadRequestError as exp:
                logging.error(exp, exc_info=True)
                return self._return_error(f"Bad request", 400)

        return blueprint



