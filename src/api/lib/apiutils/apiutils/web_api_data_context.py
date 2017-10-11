from typing import Any, Dict, List

from sqlutils import DataContext

from .request import Request


class WebApiDataContext(DataContext):

    def __init__(self, application_root: str) -> None:
        self._application_root = application_root

    def execute(self, cmd: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Custom GET request."""
        result: List[Dict[str, Any]] = []
        query = f'{self._application_root}/{cmd}?{"&".join(f"{k}={v}" for k, v in params.items())}'
        response = Request.get(query)
        if response.status_code != 200:
            return result

        data = response.json()
        if isinstance(data, list):
            return data
        else:
            result.append(data)
        return result

    def callproc(self, cmd: str, params: List[Any]) -> List[Dict[str, Any]]:
        """Custom POST request"""
        # TODO: implement post request with dictionary params
        raise NotImplementedError

    @property
    def conn_string(self) -> str:
        return self._application_root

    def get_by_id(self, collection: str, key: str = None, uid: Any = None) -> Dict[str, Any]:
        response = Request.get(f'{self._application_root}/{collection}/{uid}')
        if response.status_code != 200:
            return {}
        return response.json()

    def get_all(self, collection: str) -> List[Dict[str, Any]]:
        response = Request.get(f'{self._application_root}/{collection}/')
        if response.status_code != 200:
            return []
        return response.json()

    def add(self, collection: str, data: Dict[str, Any]) -> Any:
        response = Request.post(f'{self._application_root}/{collection}/', data=data, is_json=True)
        return response

    def update(self, collection: str, key: str, data: Dict[str, Any]) -> None:
        Request.put(f'{self._application_root}/{collection}/', data=data, is_json=True)

    def delete(self, collection: str, key: str, uid: Any) -> None:
        Request.delete(f'{self._application_root}/{collection}/{uid}')
