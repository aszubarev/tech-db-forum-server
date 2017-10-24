from sqlutils import Converter

from forum.models.forum import Forum
from forum.models.user import User
from forum.persistence.dto.forum_dto import ForumDTO


class ForumConverter(Converter[Forum, ForumDTO]):

    def convert(self, entity: ForumDTO) -> Forum:
        return Forum(uid=entity.uid).fill(
            slug=entity.slug,
            user=User(entity.user_id),
            title=entity.title
        )
