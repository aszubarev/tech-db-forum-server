import logging
from datetime import datetime

import pytz
from flask import Blueprint, abort, request, Response, json
from injector import inject, singleton

from apiutils import BaseBlueprint
from apiutils.errors.bad_request_error import BadRequestError
from forum.persistence.repositories.post_repository import PostRepository

from forum.serializers.post_serializer import PostSerializer
from forum.services.forum_service import ForumService
from forum.services.user_service import UserService
from sqlutils import NoDataFoundError
from forum.serializers.post_serializer_detail import PostSerializerFull
from forum.services.post_service import PostService
from forum.services.thread_service import ThreadService


@singleton
class PostBlueprint(BaseBlueprint[PostService]):

    @inject
    def __init__(self, service: PostService, serializer: PostSerializer,
                 post_serializer_full: PostSerializerFull,
                 thread_service: ThreadService, user_service: UserService, forum_service: ForumService,
                 post_repo: PostRepository) -> None:
        super().__init__(service)
        self._threadService = thread_service
        self.__serializer = serializer
        self._postSerializerFull = post_serializer_full
        self._userService = user_service
        self._forumService = forum_service
        self._postRepo = post_repo

        self._tz = pytz.timezone('Europe/Moscow')

    @property
    def _name(self) -> str:
        return 'posts'

    @property
    def _serializer(self) -> PostSerializer:
        return self.__serializer

    @property
    def __service(self) -> PostService:
        return self._repository

    def _create_blueprint(self) -> Blueprint:
        blueprint = Blueprint(self._name, __name__)

        @blueprint.route('thread/<slug_or_id>/create', methods=['POST'])
        def _add_many(slug_or_id: str):

            thread = self._threadService.get_by_slug_or_id(slug_or_id)
            if not thread:
                return self._return_error(f"Can't find thread by slag = {slug_or_id}", 404)

            body = request.json
            response = []

            if not body:
                return Response(response=json.dumps(response), status=201, mimetype='application/json')

            created = datetime.now(tz=self._tz).astimezone(tz=self._tz).isoformat()
            insert_values = "(post_id, thread_id, forum_id, forum_slug, user_id, user_nickname, " \
                            " parent_id, message, created, is_edited, path)"
            insert_args = ""

            for post in body:
                user_nickname = post['author']
                user = self._userService.get_by_nickname(user_nickname)
                if not user:
                    return self._return_error(f"Can't find user by nickname = {user_nickname}", 404)

                uid = self.__service.next_uid()
                parent_id = post.get('parent')

                if not parent_id:
                    parent_id = 0
                    path = "{" + str(uid) + "}"
                else:
                    parent = self._postRepo.get_parent(parent_id)
                    if not parent:
                        return self._return_error(f"Can't get parent for post", 409)

                    if parent['thread'] != thread['id']:
                        return self._return_error(f"The parent belongs to another thread: parent_id = {parent_id}", 409)

                    path = parent['path']
                    path.append(uid)
                    path = str(path).replace('[', '{').replace(']', '}')

                is_edited = False
                args = f"({uid}, {thread['id']}, {thread['forum_id']}, E\'{thread['forum']}\', " \
                       f" {user['user_id']}, E\'{user['nickname']}\'," \
                       f" {parent_id}, E\'{post['message']}\', E\'{created}\', E\'{is_edited}\', E\'{path}\')"

                if not insert_args:
                    insert_args = args
                else:
                    insert_args += ", " + args

                data = {
                    'id': uid,
                    'thread': thread['id'],
                    'author': user['nickname'],
                    'forum': thread['forum'],
                    'parent': parent_id,
                    'message': post['message'],
                    'isEdited': is_edited,
                    'created': created
                }
                response.append(data)

            self.__service.add_many(insert_values=insert_values, insert_args=insert_args)
            self._forumService.increment_posts_by_number(thread['forum_id'], len(response))
            return Response(response=json.dumps(response), status=201, mimetype='application/json')

        @blueprint.route('thread/<slug_or_id>/posts', methods=['GET'])
        def _posts(slug_or_id: str):
            try:

                thread = self._threadService.get_by_slug_or_id_setup(slug_or_id, load_forum=True)
                if not thread:
                    return self._return_error(f"Can't get thread by forum slug_or_id = {slug_or_id}", 404)

                response = self.__service.get_posts_for_thread(thread.uid)
                return Response(response=json.dumps(response), status=200, mimetype='application/json')

            except NoDataFoundError as exp:
                return self._return_error(f"Can't get thread by forum slug_or_id = {slug_or_id}", 404)

            except BadRequestError as exp:
                return self._return_error(f"Bad request", 400)

        @blueprint.route('post/<uid>/details', methods=['GET'])
        def _details(uid: int):
            post = self.__service.get_by_id(uid)

            if not post:
                return self._return_error(f"Can't find post by id = {uid}", 404)

            author = None
            forum = None
            thread = None

            related = request.args.get('related')

            if related is not None:

                if 'user' in related:
                    author = self._userService.get_by_id(post['user_id'])

                if 'thread' in related:
                    thread = self._threadService.get_by_id(post['thread'])

                if 'forum' in related:
                    forum = self._forumService.get_by_id(post['forum_id'])

            response = {
                'author': author,
                'thread': thread,
                'forum': forum,
                'post': post
            }

            return Response(response=json.dumps(response), status=200, mimetype='application/json')

        @blueprint.route('post/<uid>/details', methods=['POST'])
        def _update(uid: int):

            data = request.json

            # empty request
            if not data:
                post = self.__service.get_by_id(uid)
                if not post:
                    return self._return_error(f"Can't get post by uid = {uid}", 404)
                return Response(response=json.dumps(post), status=200, mimetype='application/json')

            message = data['message']
            response = self.__service.update_soft(uid=uid, message=message)

            if not response:
                return self._return_error(f"Can't find post by uid = {uid}", 404)

            return Response(response=json.dumps(response), status=200, mimetype='application/json')

        return blueprint