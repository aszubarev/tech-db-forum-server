from abc import abstractmethod
import logging
from typing import List, Any, TypeVar, Generic, Dict, Optional

from flask import abort, json, request, url_for, Blueprint, Response

from sqlutils import Model, Service
from sqlutils import ForeignKeyViolationError, NoDataFoundError, UniqueViolationError

from .serializer import Serializer

T = TypeVar("T", bound="Model")
S = TypeVar("S", bound="Service")

class Error(object):

    def __init__(self, msg: str) -> None:
        self._msg: str = msg

    @property
    def msg(self) -> str:
        return self._msg


class ErrorSerializer(object):

    @staticmethod
    def dump(model: Error) -> Optional[Dict[str, Any]]:

        if not model:
            return None

        data = {
            'message': model.msg
        }

        return data


def return_one(model: Model, serializer: Serializer, **kwargs) -> Response:
    if model is None:
        abort(404)

    response = serializer.dump(model, **kwargs)

    status = kwargs.get('status')
    if status is None:
        status = 200

    return Response(response=json.dumps(response),
                    status=status, mimetype='application/json')


def return_many(models: List[T], serializer: Serializer, **kwargs) -> Response:
    response = []
    for model in models:
        response.append(serializer.dump(model))

    sort_key = kwargs.get('sort_key')
    sort_reverse = kwargs.get('sort_reverse')
    if sort_key is not None and sort_reverse is not None:
        sorted(models, key=sort_key, reverse=sort_reverse)
    elif sort_key is not None and sort_reverse is None:
        sorted(models, key=sort_key)

    status = kwargs.get('status')
    if status is None:
        status = 200

    return Response(response=json.dumps(response),
                    status=status, mimetype='application/json')


class BaseBlueprint(Generic[S]):

    def __init__(self, service: S) -> None:
        self._blueprint = None
        self._service = service
        self._error_serializer = ErrorSerializer

    @property
    @abstractmethod
    def _name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def _serializer(self) -> Serializer:
        raise NotImplementedError

    @property
    def blueprint(self) -> Blueprint:
        if not self._blueprint:
            self._blueprint = self._create_blueprint()
        return self._blueprint

    def _return_one(self, model: Model, **kwargs) -> Response:
        return return_one(model, self._serializer, **kwargs)

    def _return_many(self, models: List[Model], **kwargs) -> Response:
        return return_many(models, self._serializer, **kwargs)

    def _get_by_id(self, uid: Any):
        model = None
        try:
            model = self._service.get_by_id(uid)
        except BaseException:
            logging.exception("Can't get {0} model by id".format(self._name))
            abort(400)
        return self._return_one(model)

    def _get_all(self):
        try:
            models = self._service.get_all()
            return self._return_many(models)
        except BaseException:
            logging.exception("Can't get all {0} models".format(self._name))
            abort(500)

    def _add(self, **kwargs):
        entity = self._parse(**kwargs)
        model = self._add_entity(entity)
        response = self._serializer.dump(model)

        status = kwargs.get('status')
        if not status:
            status = 201

        return Response(response=json.dumps(response), status=status, mimetype='application/json')

    def _add_many(self, **kwargs):
        entities = self._parse_many(**kwargs)
        models = self._add_many_entity(entities)
        return self._return_many(models, status=201)

    def _update(self, **kwargs):
        entity = self._parse(**kwargs)
        model = self._update_entity(entity)
        response = self._serializer.dump(model)
        return Response(response=json.dumps(response), status=200, mimetype='application/json')

    def _delete(self, uid: Any) -> Response:
        model: Model = None
        try:
            model = self._service.get_by_id(uid)
        except BaseException:
            logging.exception("Can't get {0} model".format(self._name))
            abort(400)

        if model is None:
            abort(404)

        self._service.delete(model.uid)
        return Response(response='', status=204, mimetype='application/json')

    def _return_error(self, msg: str, status):
        response = self._error_serializer.dump(Error(msg))
        return Response(response=json.dumps(response), status=status, mimetype='application/json')

    @abstractmethod
    def _create_blueprint(self) -> Blueprint:
        raise NotImplementedError

    def _parse(self, **kwargs):

        entity = None
        try:

            load_data = request.json
            load_data.update(kwargs)
            entity = self._serializer.load(load_data)
        except NoDataFoundError as exp:
            raise NoDataFoundError(f"Can't parse {self._name} entity") from exp
        except BaseException:
            logging.exception(f"Can't parse {self._name} entity")
            abort(400)
        return entity

    def _parse_many(self, **kwargs):

        entities = []

        prepared_load_data = self._serializer.prepare_load_data(**kwargs)

        load_data_list = request.json
        if not load_data_list:
            return entities

        for load_data in load_data_list:
            load_data.update(prepared_load_data)
            entity = self._serializer.load(load_data)
            entities.append(entity)

        # except NoDataFoundError as exp:
        #     raise NoDataFoundError(f"Can't parse {self._name} entity") from exp

        # except BaseException:
        #     logging.exception(f"Can't parse {self._name} entity")
        #     abort(400)
        return entities

    def _add_entity(self, entity: Any) -> Any:

        try:
            model = self._service.add(entity)
            if model is None:
                raise NoDataFoundError("Can't add {0} entity".format(self._name))

            return model

        except NoDataFoundError as exp:
            raise NoDataFoundError("Can't add {0} entity".format(self._name)) from exp

        except UniqueViolationError as exp:
            raise UniqueViolationError(f"Can't add {self._name} entity") from exp

        except ForeignKeyViolationError as exp:
            raise ForeignKeyViolationError(f"Can't add {self._name} entity") from exp

    def _update_entity(self, entity: Any) -> Any:
        try:
            model = self._service.update(entity)
            if model is None:
                raise NoDataFoundError("Can't add {0} entity".format(self._name))

            return model

        except NoDataFoundError as exp:
            raise NoDataFoundError("Can't update {0} entity".format(self._name)) from exp

        except UniqueViolationError as exp:
            raise UniqueViolationError(f"Can't update {self._name} entity") from exp

        except ForeignKeyViolationError as exp:
            raise ForeignKeyViolationError(f"Can't update {self._name} entity") from exp

    def _add_many_entity(self, entities: List[Any]) -> List[Any]:

        try:
            models = self._service.add_many(entities)
            return models

        except NoDataFoundError as exp:
            raise NoDataFoundError("Can't add {0} entity".format(self._name)) from exp

        except UniqueViolationError as exp:
            raise UniqueViolationError(f"Can't add {self._name} entity") from exp

        except ForeignKeyViolationError as exp:
            raise ForeignKeyViolationError(f"Can't add {self._name} entity") from exp


