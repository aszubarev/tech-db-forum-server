from typing import Dict, Any, Optional

from injector import inject, singleton

from apiutils import Serializer

from forum.models.service import Srv


@singleton
class SrvSerializer(Serializer):

    @inject
    def __init__(self):
        pass

    def dump(self, model: Srv, **kwargs) -> Optional[Dict[str, Any]]:

        if not model:
            return None

        data = {}

        if model.is_loaded:
            data.update({
                'forum': model.forums,
                'thread': model.threads,
                'post': model.posts,
                'user': model.users,
            })

        return data

    def prepare_load_data(self, **kwargs):
        raise NotImplementedError

    def load(self, data: Dict[str, Any]):
        raise NotImplementedError
