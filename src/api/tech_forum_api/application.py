from flask import Flask
from injector import inject, singleton

from tech_forum_api.blueprints.user_blueprint import UserBlueprint
from tech_forum_api.ioc import ioc


class Application(object):

    @inject
    def __init__(self) -> None:
        self._users = ioc.get(UserBlueprint, scope=singleton).blueprint

    def register(self, app: Flask) -> None:
        app.register_blueprint(self._users, url_prefix='/user')

