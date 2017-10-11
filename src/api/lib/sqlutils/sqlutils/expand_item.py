from typing import Optional


class ExpandItem(object):

    def __init__(self, name: str, child: "ExpandItem" = None) -> None:
        self._name = name
        self._child = child

    @property
    def name(self) -> str:
        return self._name

    @property
    def child(self) -> "ExpandItem":
        return self._child

    @staticmethod
    def load(expand: str) -> Optional["ExpandItem"]:
        if not expand:
            return None

        items = expand.split('.')
        name = items[0]
        child = ExpandItem.load('.'.join(items[1:]))
        return ExpandItem(name, child)

    def __str__(self) -> str:
        name = self.name
        if self._child:
            name += '.' + str(self.child)
        return name
