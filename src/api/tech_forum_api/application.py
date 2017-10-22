from flask import Flask
from injector import inject, singleton

from tech_forum_api.blueprints.forum_blueprint import ForumBlueprint
from tech_forum_api.blueprints.post_blueprint import PostBlueprint
from tech_forum_api.blueprints.service_blueprint import SrvBlueprint
from tech_forum_api.blueprints.thread_blueprint import ThreadBlueprint
from tech_forum_api.blueprints.user_blueprint import UserBlueprint
from tech_forum_api.blueprints.vote_blueprint import VoteBlueprint
from tech_forum_api.ioc import ioc


class Application(object):

    @inject
    def __init__(self) -> None:
        self._users = ioc.get(UserBlueprint, scope=singleton).blueprint
        self._forums = ioc.get(ForumBlueprint, scope=singleton).blueprint
        self._threads = ioc.get(ThreadBlueprint, scope=singleton).blueprint
        self._posts = ioc.get(PostBlueprint, scope=singleton).blueprint
        self._votes = ioc.get(VoteBlueprint, scope=singleton).blueprint
        self._service = ioc.get(SrvBlueprint, scope=singleton).blueprint

    def register(self, app: Flask) -> None:
        app.register_blueprint(self._users, url_prefix='/')
        app.register_blueprint(self._forums, url_prefix='/')
        app.register_blueprint(self._threads, url_prefix='/')
        app.register_blueprint(self._posts, url_prefix='/')
        app.register_blueprint(self._votes, url_prefix='/')
        app.register_blueprint(self._service, url_prefix='/')

