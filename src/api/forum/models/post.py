from datetime import datetime
from typing import List

from sqlutils import Model
from forum.models.user import User
from forum.models.forum import Forum
from forum.models.thread import Thread


class Post(Model):

    def __init__(self, uid: int) -> None:
        super().__init__(uid)

        self._thread: Thread = None
        self._forum: Forum = None
        self._author: User = None
        self._parent: Post = None
        self._message: str = None
        self._created: datetime = None
        self._is_edited: bool = None
        self._path: List[int] = None

    @property
    def thread(self) -> Thread:
        return self._thread

    @property
    def forum(self) -> Forum:
        return self._forum

    @property
    def author(self) -> User:
        return self._author

    @property
    def parent(self) -> "Post":
        return self._parent

    @property
    def message(self) -> str:
        return self._message

    @property
    def created(self) -> datetime:
        return self._created

    @property
    def is_edited(self) -> bool:
        return self._is_edited

    @property
    def path(self) -> List[int]:
        return self._path

    def fill(self, thread: Thread, forum: Forum, author: User, parent: "Post",
             message: str, created: datetime, is_edited: bool, path: List[int]) -> "Post":
        self._thread = thread
        self._forum = forum
        self._author = author
        self._parent = parent
        self._message = message
        self._created = created
        self._is_edited = is_edited
        self._path = path
        self._filled()
        return self
