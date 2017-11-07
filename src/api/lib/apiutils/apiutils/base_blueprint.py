from abc import abstractmethod
from typing import TypeVar, Generic

from flask import json, Blueprint, Response

R = TypeVar("R", bound="Repository")


class BaseBlueprint(Generic[R]):

    def __init__(self, repo: R) -> None:
        self._blueprint = None
        self._repo = repo

    @property
    @abstractmethod
    def _name(self) -> str:
        raise NotImplementedError

    @property
    def blueprint(self) -> Blueprint:
        if not self._blueprint:
            self._blueprint = self._create_blueprint()
        return self._blueprint

    @staticmethod
    def _return_error(msg: str, status):
        return Response(response=json.dumps({'msg': msg}), status=status, mimetype='application/json')

    @abstractmethod
    def _create_blueprint(self) -> Blueprint:
        raise NotImplementedError




