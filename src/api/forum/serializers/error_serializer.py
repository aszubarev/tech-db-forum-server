from typing import Dict, Any, Optional
from forum.models.error import Error


class ErrorSerializer(object):

    @staticmethod
    def dump(model: Error) -> Optional[Dict[str, Any]]:

        if not model:
            return None

        data = {
            'message': model.msg
        }

        return data


