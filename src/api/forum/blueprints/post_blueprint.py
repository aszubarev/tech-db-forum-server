import logging
from datetime import datetime

import pytz
from flask import Blueprint, request, Response, json
from injector import inject, singleton

from apiutils import BaseBlueprint
from apiutils.errors.bad_request_error import BadRequestError
from forum.persistence.repositories.forum_repository import ForumRepository
from forum.persistence.repositories.post_repository import PostRepository
from forum.persistence.repositories.thread_repository import ThreadRepository
from forum.persistence.repositories.user_repository import UserRepository

from sqlutils import NoDataFoundError


@singleton
class PostBlueprint(BaseBlueprint[PostRepository]):

    @inject
    def __init__(self, repo: PostRepository,
                 thread_repo: ThreadRepository, user_repo: UserRepository, forum_repo: ForumRepository) -> None:
        super().__init__(repo)
        self._threadRepo = thread_repo
        self._userRepo = user_repo
        self._forumRepo = forum_repo

        self._tz = pytz.timezone('Europe/Moscow')

    @property
    def _name(self) -> str:
        return 'posts'

    @property
    def __repo(self) -> PostRepository:
        return self._repo

    def _create_blueprint(self) -> Blueprint:
        blueprint = Blueprint(self._name, __name__)

        @blueprint.route('thread/<slug_or_id>/create', methods=['POST'])
        def _add_many(slug_or_id: str):

            thread = self._threadRepo.get_by_slug_or_id(slug_or_id)
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
                user = self._userRepo.get_by_nickname(user_nickname)
                if not user:
                    return self._return_error(f"Can't find user by nickname = {user_nickname}", 404)

                uid = self.__repo.next_uid()
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

            self.__repo.add_many(insert_values=insert_values, insert_args=insert_args)
            self._forumRepo.increment_posts_by_number(thread['forum_id'], len(response))
            return Response(response=json.dumps(response), status=201, mimetype='application/json')

        @blueprint.route('thread/<slug_or_id>/posts', methods=['GET'])
        def _posts(slug_or_id: str):
            try:

                thread = self._threadRepo.get_by_slug_or_id(slug_or_id)
                if not thread:
                    return self._return_error(f"Can't get thread by forum slug_or_id = {slug_or_id}", 404)

                response = self.__repo.get_posts_for_thread(thread['id'])
                return Response(response=json.dumps(response), status=200, mimetype='application/json')

            except NoDataFoundError:
                return self._return_error(f"Can't get thread by forum slug_or_id = {slug_or_id}", 404)

            except BadRequestError:
                return self._return_error(f"Bad request", 400)

        @blueprint.route('post/<uid>/details', methods=['GET'])
        def _details(uid: int):
            post = self.__repo.get_by_id(uid)

            if not post:
                return self._return_error(f"Can't find post by id = {uid}", 404)

            author = None
            forum = None
            thread = None

            related = request.args.get('related')

            if related is not None:

                if 'user' in related:
                    author = self._userRepo.get_by_id(post['user_id'])

                if 'thread' in related:
                    thread = self._threadRepo.get_by_id(post['thread'])

                if 'forum' in related:
                    forum = self._forumRepo.get_by_id(post['forum_id'])

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
                post = self.__repo.get_by_id(uid)
                if not post:
                    return self._return_error(f"Can't get post by uid = {uid}", 404)
                return Response(response=json.dumps(post), status=200, mimetype='application/json')

            message = data['message']
            response = self.__repo.update(uid=uid, message=message)

            if not response:
                return self._return_error(f"Can't find post by uid = {uid}", 404)

            return Response(response=json.dumps(response), status=200, mimetype='application/json')

        return blueprint
