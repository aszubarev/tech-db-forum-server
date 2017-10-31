from abc import abstractmethod
from typing import Any, Dict


class SoftSerializer(object):

    @abstractmethod
    def dump(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        raise NotImplementedError
