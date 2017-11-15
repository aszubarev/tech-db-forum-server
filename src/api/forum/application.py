from flask import Flask
from injector import inject, singleton

from forum.blueprints.forum_blueprint import ForumBlueprint
from forum.blueprints.post_blueprint import PostBlueprint
from forum.blueprints.service_blueprint import SrvBlueprint
from forum.blueprints.thread_blueprint import ThreadBlueprint
from forum.blueprints.user_blueprint import UserBlueprint
from forum.ioc import ioc


class Application(object):

    @inject
    def __init__(self) -> None:
        self._users = ioc.get(UserBlueprint, scope=singleton).blueprint
        self._forums = ioc.get(ForumBlueprint, scope=singleton).blueprint
        self._threads = ioc.get(ThreadBlueprint, scope=singleton).blueprint
        self._posts = ioc.get(PostBlueprint, scope=singleton).blueprint
        self._service = ioc.get(SrvBlueprint, scope=singleton).blueprint

    def register(self, app: Flask) -> None:
        app.register_blueprint(self._users, url_prefix='/api/')
        app.register_blueprint(self._forums, url_prefix='/api/')
        app.register_blueprint(self._threads, url_prefix='/api/')
        app.register_blueprint(self._posts, url_prefix='/api/')
        app.register_blueprint(self._service, url_prefix='/api/')

