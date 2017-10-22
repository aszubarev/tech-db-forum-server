import logging

from flask import Blueprint, abort, request, Response, json
from injector import inject, singleton

from apiutils import BaseBlueprint
from sqlutils import NoDataFoundError, UniqueViolationError
from tech_forum_api.serializers.service_serializer import SrvSerializer
from tech_forum_api.services.srv_service import SrvService

logging.basicConfig(level=logging.INFO)


@singleton
class SrvBlueprint(BaseBlueprint[SrvService]):

    @inject
    def __init__(self, service: SrvService, serializer: SrvSerializer) -> None:
        super().__init__(service)
        self.__serializer = serializer

    @property
    def _name(self) -> str:
        return 'service'

    @property
    def __service(self) -> SrvService:
        return self._service

    @property
    def _serializer(self) -> SrvSerializer:
        return self.__serializer

    def _create_blueprint(self) -> Blueprint:
        blueprint = Blueprint(self._name, __name__)

        @blueprint.route('service/status', methods=['GET'])
        def _status():
            model = self.__service.status()
            return self._return_one(model, status=200)

        @blueprint.route('service/clear', methods=['POST'])
        def _clear():
            self.__service.clear()
            return Response(response="Complete clear", status=200, mimetype='application/json')

        return blueprint
