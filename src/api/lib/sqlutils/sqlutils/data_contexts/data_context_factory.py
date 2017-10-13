from abc import ABCMeta
from abc import abstractmethod


class DataContextFactory(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def create_data_context(self):
        """
        :rtype: DataContext
        """
        return NotImplemented
