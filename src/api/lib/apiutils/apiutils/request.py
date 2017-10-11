import os

import requests
from flask import json
from requests import Response
from typing import Dict, Any, Tuple


class Request(object):

    proxies = {'http': ''}
    headers = {}

    proxy = os.environ.get('RT-Proxy')
    if proxy is not None:
        proxies['http'] = proxy

    authorization = os.environ.get('RT-Authorization')
    if authorization is not None:
        headers['Authorization'] = authorization

    @staticmethod
    def get(url: str) -> Response:
        return requests.get(url, proxies=Request.proxies, headers=Request.headers)

    @staticmethod
    def post(url: str, data: Dict[str, Any] = None, is_json: bool = True, files=None) -> Response:
        headers, data = Request._prepare_data(data, is_json)
        return requests.post(url, data=data, proxies=Request.proxies, headers=headers, files=files)

    @staticmethod
    def delete(url: str) -> Response:
        return requests.delete(url, proxies=Request.proxies, headers=Request.headers)

    @staticmethod
    def put(url: str, data: Dict[str, Any] = None, is_json: bool = True, files=None) -> Response:
        headers, data = Request._prepare_data(data, is_json)
        return requests.put(url, data=data, proxies=Request.proxies, headers=headers, files=files)

    @staticmethod
    def _prepare_data(data: Dict[str, Any], is_json: bool) -> Tuple[Dict[str, str], Dict[str, Any]]:
        headers = Request.headers
        if is_json:
            headers['content-type'] = 'application/json'
            data = json.dumps(data)
        return headers, data
