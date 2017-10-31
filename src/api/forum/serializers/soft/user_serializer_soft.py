from typing import Dict, Any, Optional

from injector import inject, singleton

from apiutils import SoftSerializer


@singleton
class UserSerializerSoft(SoftSerializer):

    @inject
    def __init__(self):
        pass

    def dump(self, data: Dict[str, Any], **kwargs) -> Optional[Dict[str, Any]]:

        if not data:
            return None

        response = {
            'nickname': data['nickname'],
            'email': data['email'],
            'about': data['about'],
            'fullname': data['fullname'],
        }

        return response
