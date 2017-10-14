from sqlutils import Converter

from tech_forum_api.models.forum import Forum
from tech_forum_api.models.user import User
from tech_forum_api.persistence.dto.forum_dto import ForumDTO


class ForumConverter(Converter[Forum, ForumDTO]):

    def convert(self, entity: ForumDTO) -> Forum:
        return Forum(uid=entity.uid).fill(
            slug=entity.slug,
            user=User(entity.user_id),
            title=entity.title
        )
