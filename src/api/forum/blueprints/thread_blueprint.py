import dateutil.parser
from flask import Blueprint, abort, request, Response, json
from injector import inject, singleton

from apiutils import BaseBlueprint
from apiutils.errors.bad_request_error import BadRequestError
from forum.persistence.repositories.thread_repository import ThreadRepository

from forum.serializers.thread_serializer import ThreadSerializer
from forum.serializers.vote_serializer import VoteSerializer
from sqlutils import NoDataFoundError, UniqueViolationError
from forum.services.forum_service import ForumService
from forum.services.thread_service import ThreadService
from forum.services.user_service import UserService


@singleton
class ThreadBlueprint(BaseBlueprint[ThreadRepository]):

    @inject
    def __init__(self, repo: ThreadRepository, serializer: ThreadSerializer, vote_serializer: VoteSerializer,
                 user_service: UserService, forum_service: ForumService) -> None:
        super().__init__(repo)
        self.__serializer = serializer
        self._userService = user_service
        self._forumService = forum_service
        self._voteSerializer = vote_serializer

    @property
    def _name(self) -> str:
        return 'threads'

    @property
    def _serializer(self) -> ThreadSerializer:
        return self.__serializer

    @property
    def __service(self) -> ThreadService:
        return self._repository

    def _create_blueprint(self) -> Blueprint:
        blueprint = Blueprint(self._name, __name__)

        @blueprint.route('forum/<slug>/create', methods=['POST'])
        def _add(slug: str):
            try:
                body = request.json
                author = self._userService.get_by_nickname(body.get('author'))
                if not author:
                    return self._return_error(f"Can't find author for thread by nickname = {body.get('author')}", 404)

                forum = self._forumService.get_by_slug(slug)
                if not forum:
                    return self._return_error(f"Can't find forum for thread by slug = {slug}", 404)

                response = self.__service.add_soft(body=body,
                                                   user_id=author['user_id'], user_nickname=author['nickname'],
                                                   forum_id=forum['forum_id'], forum_slug=forum['slug'])

                return Response(response=json.dumps(response), status=201, mimetype='application/json')

            except UniqueViolationError:
                thread_slug = request.json['slug']
                response = self._repository.get_by_slug(thread_slug)
                return Response(response=json.dumps(response), status=409, mimetype='application/json')

        @blueprint.route('forum/<slug>/threads', methods=['GET'])
        def _get_threads_by_forum(slug: str):

            forum = self._forumService.get_by_slug(slug)
            if forum is None:
                return self._return_error(f"Can't get threads by forum slag = {slug}", 404)

            desc = request.args.get('desc')
            limit = request.args.get('limit')
            since = request.args.get('since')
            if since is not None:
                since = dateutil.parser.parse(since)

            threads = self.__service.get_for_forum(forum['forum_id'], since=since, limit=limit, desc=desc)
            return Response(response=json.dumps(threads), status=200, mimetype='application/json')

        @blueprint.route('thread/<slug_or_id>/details', methods=['GET'])
        def _details(slug_or_id: str):

            thread = self.__service.get_by_slug_or_id(slug_or_id)
            if not thread:
                return self._return_error(f"Can't get thread by forum slug_or_id = {slug_or_id}", 404)
            return Response(response=json.dumps(thread), status=200, mimetype='application/json')

        @blueprint.route('thread/<slug_or_id>/details', methods=['POST'])
        def _update(slug_or_id: str):
            try:

                data = request.json

                # empty request
                if not data:
                    thread = self.__service.get_by_slug_or_id(slug_or_id)
                    if not thread:
                        return self._return_error(f"Can't get thread by slug_or_id = {slug_or_id}", 404)
                    return Response(response=json.dumps(thread), status=200, mimetype='application/json')

                try:

                    cast_thread_id = int(slug_or_id)

                    data.update({
                        'id': cast_thread_id
                    })

                    entity = self._serializer.load(data)
                    thread = self.__service.update_by_uid(entity)

                except ValueError:
                    thread_slug = slug_or_id

                    data.update({
                        'slug': thread_slug
                    })

                    entity = self._serializer.load(data)
                    thread = self.__service.update_by_slug(entity)

                if not thread:
                    return self._return_error(f"Can't update thread by slug_or_id = {slug_or_id}", 404)

                return self._return_one(thread, status=200)

            except NoDataFoundError as exp:
                return self._return_error(f"Can't update thread by forum slug_or_id = {slug_or_id}", 404)

            except BadRequestError as exp:
                return self._return_error(f"Bad request", 400)

        @blueprint.route('thread/<slug_or_id>/vote', methods=['POST'])
        def _vote(slug_or_id: str):
            try:

                data = request.json
                nickname = data.get('nickname')
                voice = data.get('voice')
                if not nickname or not voice:
                    return self._return_error(f"[ThreadBlueprint._vote] Bad request", 400)

                thread = self._repository.get_by_slug_or_id(slug_or_id)
                if not thread:
                    return self._return_error(f"Can't find thread by slug_or_id = {slug_or_id}", 404)

                user = self._userService.get_by_nickname(nickname)
                if not user:
                    return self._return_error(f"Can't find user by nickname = {nickname}", 404)

                data.update({
                    'thread_id': thread['id'],
                    'user_id': user['user_id'],
                })

                entity = self._voteSerializer.load(data)
                votes = self.__service.vote(entity)
                if votes is None:
                    return self._return_error(f"[ThreadBlueprint._vote] "
                                              f"Can't get votes for thread by slug_or_id = {slug_or_id}", 500)

                thread['votes'] = votes
                return Response(response=json.dumps(thread), status=200, mimetype='application/json')

            except NoDataFoundError as exp:
                return self._return_error(f"Can't create thread by request = {request.json}", 404)

        return blueprint



