from injector import inject
from sqlutils import DataContext


class VoteRepository(object):

    @inject
    def __init__(self, context: DataContext) -> None:
        self._context = context

    def clear(self):
        self._context.callproc('clear_vote', [])
