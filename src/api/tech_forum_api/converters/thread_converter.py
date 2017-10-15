from sqlutils import Converter
from tech_forum_api.models.user import User
from tech_forum_api.models.forum import Forum
from tech_forum_api.models.thread import Thread
from tech_forum_api.persistence.dto.thread_dto import ThreadDTO


class ThreadConverter(Converter[Thread, ThreadDTO]):

    def convert(self, entity: ThreadDTO) -> Thread:
        return Thread(uid=entity.uid).fill(
            slug=entity.slug,
            forum=Forum(entity.forum_id),
            author=User(entity.user_id),
            created=entity.created,
            message=entity.message,
            title=entity.title
        )
