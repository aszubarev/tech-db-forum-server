from sqlutils import Converter
from forum.models.post import Post
from forum.models.user import User
from forum.models.forum import Forum
from forum.models.thread import Thread
from forum.persistence.dto.post_dto import PostDTO


class PostConverter(Converter[Post, PostDTO]):

    def convert(self, entity: PostDTO) -> Post:
        return Post(uid=entity.uid).fill(
            thread=Thread(entity.thread_id),
            forum=Forum(entity.forum_id).fill(slug=entity.forum_slug),
            author=User(entity.user_id).fill(nickname=entity.user_nickname),
            parent=Post(entity.parent_id),
            message=entity.message,
            created=entity.created,
            is_edited=entity.is_edited,
            path=entity.path
        )
