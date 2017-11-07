import dateutil.parser
from flask import Blueprint, request, Response, json
from injector import inject, singleton

from apiutils import BaseBlueprint
from forum.persistence.repositories.forum_repository import ForumRepository
from forum.persistence.repositories.thread_repository import ThreadRepository
from forum.persistence.repositories.user_repository import UserRepository
from sqlutils import UniqueViolationError


@singleton
class ThreadBlueprint(BaseBlueprint[ThreadRepository]):

    @inject
    def __init__(self, repo: ThreadRepository, user_repo: UserRepository, forum_repo: ForumRepository) -> None:
        super().__init__(repo)
        self._userRepo = user_repo
        self._forumRepo = forum_repo

    @property
    def _name(self) -> str:
        return 'threads'

    @property
    def __repo(self) -> ThreadRepository:
        return self._repo

    def _create_blueprint(self) -> Blueprint:
        blueprint = Blueprint(self._name, __name__)

        @blueprint.route('forum/<slug>/create', methods=['POST'])
        def _add(slug: str):
            try:
                body = request.json
                author = self._userRepo.get_by_nickname(body.get('author'))
                if not author:
                    return self._return_error(f"Can't find author for thread by nickname = {body.get('author')}", 404)

                forum = self._forumRepo.get_by_slug(slug)
                if not forum:
                    return self._return_error(f"Can't find forum for thread by slug = {slug}", 404)

                params = body
                forum_id = forum['forum_id']
                params.update({
                    'user_id': author['user_id'],
                    'user_nickname': author['nickname'],
                    'forum_id': forum_id,
                    'forum_slug': forum['slug'],
                    'slug': None if body.get('slug') is None else body['slug'],
                    'created': None if body.get('created') is None else dateutil.parser.parse(body['created'])
                })
                response = self.__repo.add(params)
                self._forumRepo.increment_threads(uid=forum_id)
                return Response(response=json.dumps(response), status=201, mimetype='application/json')

            except UniqueViolationError:
                thread_slug = request.json['slug']
                response = self.__repo.get_by_slug(thread_slug)
                return Response(response=json.dumps(response), status=409, mimetype='application/json')

        @blueprint.route('forum/<slug>/threads', methods=['GET'])
        def _get_threads_by_forum(slug: str):

            forum = self._forumRepo.get_by_slug(slug)
            if forum is None:
                return self._return_error(f"Can't get threads by forum slag = {slug}", 404)

            desc = request.args.get('desc')
            limit = request.args.get('limit')
            since = request.args.get('since')
            if since is not None:
                since = dateutil.parser.parse(since)

            threads = self.__repo.get_for_forum(forum['forum_id'], since=since, limit=limit, desc=desc)
            return Response(response=json.dumps(threads), status=200, mimetype='application/json')

        @blueprint.route('thread/<slug_or_id>/details', methods=['GET'])
        def _details(slug_or_id: str):

            thread = self.__repo.get_by_slug_or_id(slug_or_id)
            if not thread:
                return self._return_error(f"Can't get thread by forum slug_or_id = {slug_or_id}", 404)
            return Response(response=json.dumps(thread), status=200, mimetype='application/json')

        @blueprint.route('thread/<slug_or_id>/details', methods=['POST'])
        def _update(slug_or_id: str):

            body = request.json

            # empty request
            if not body:
                thread = self.__repo.get_by_slug_or_id(slug_or_id)
                if not thread:
                    return self._return_error(f"Can't get thread by slug_or_id = {slug_or_id}", 404)
                return Response(response=json.dumps(thread), status=200, mimetype='application/json')

            thread = self.__repo.update_by_slug_or_id(slug_or_id=slug_or_id,
                                                      msg=body.get('message'),
                                                      title=body.get('title'))

            if not thread:
                return self._return_error(f"Can't update thread by slug_or_id = {slug_or_id}", 404)

            return self._return_one(thread, status=200)

        @blueprint.route('thread/<slug_or_id>/vote', methods=['POST'])
        def _vote(slug_or_id: str):

            data = request.json
            nickname = data.get('nickname')
            voice = data.get('voice')
            if not nickname or not voice:
                return self._return_error(f"[ThreadBlueprint._vote] Bad request", 400)

            thread = self.__repo.get_by_slug_or_id(slug_or_id)
            if not thread:
                return self._return_error(f"Can't find thread by slug_or_id = {slug_or_id}", 404)

            user = self._userRepo.get_by_nickname(nickname)
            if not user:
                return self._return_error(f"Can't find user by nickname = {nickname}", 404)

            votes = self.__repo.vote(user_id=user['user_id'], thread_id=thread['id'], voice=voice)
            if votes is None:
                return self._return_error(f"[ThreadBlueprint._vote] "
                                          f"Can't get votes for thread by slug_or_id = {slug_or_id}", 500)

            thread['votes'] = votes
            return Response(response=json.dumps(thread), status=200, mimetype='application/json')

        return blueprint



