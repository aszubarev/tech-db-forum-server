from sqlutils import Converter
from tech_forum_api.models.post import Post
from tech_forum_api.models.user import User
from tech_forum_api.models.forum import Forum
from tech_forum_api.models.thread import Thread
from tech_forum_api.persistence.dto.post_dto import PostDTO


class PostConverter(Converter[Post, PostDTO]):

    def convert(self, entity: PostDTO) -> Post:
        return Post(uid=entity.uid).fill(
            thread=Thread(entity.thread_id),
            forum=Forum(entity.forum_id),
            author=User(entity.user_id),
            parent=Post(entity.parent_id),
            message=entity.message,
            created=entity.created,
            is_edited=entity.is_edited,
            path=entity.path
        )
