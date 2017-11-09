from injector import inject, singleton
from sqlutils import DataContext


@singleton
class VoteRepository(object):

    @inject
    def __init__(self, context: DataContext) -> None:
        self._context = context

    def clear(self):
        self._context.callproc('clear_vote', [])
