from typing import Dict, Any, Optional

from injector import inject, singleton

from apiutils import Serializer

from forum.models.forum import Forum
from forum.persistence.dto.forum_dto import ForumDTO
from forum.services.post_service import PostService
from forum.services.thread_service import ThreadService
from forum.services.user_service import UserService
from sqlutils import NoDataFoundError


@singleton
class ForumSerializer(Serializer):

    @inject
    def __init__(self, user_service: UserService, thread_service: ThreadService, post_service: PostService):
        self._userService = user_service
        self._threadService = thread_service
        self._postService = post_service

    def dump(self, model: Forum, **kwargs) -> Optional[Dict[str, Any]]:

        if not model:
            return None

        data = {}
        user = self._userService.get_by_id(model.user.uid)

        if model.is_loaded:
            data.update({
                'slug': model.slug,
                'title': model.title,
                'user': user.nickname
            })

        expand_details = kwargs.get("expand_details")
        if expand_details is not None:
            if expand_details is True:

                numb_threads = self._threadService.get_number_threads_for_forum(model.uid)
                numb_posts = self._postService.get_number_posts_for_forum(model.uid)

                data.update({
                    'threads': numb_threads,
                    'posts': numb_posts
                })

        return data

    def prepare_load_data(self, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError

    # TODO move to upper level
    def load(self, data: Dict[str, Any]) -> ForumDTO:

        user = self._userService.get_by_nickname(data.get('user'))
        if not user:
            raise NoDataFoundError(f"Can't find user by nickname = {data.get('user')}")

        forum_id = None if data.get('id') is None else int(data['id'])
        slug = None if data.get('slug') is None else data['slug']
        user_id = user.uid
        title = None if data.get('title') is None else data['title']

        return ForumDTO(forum_id, slug, user_id, title)
