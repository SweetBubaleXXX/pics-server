from abc import ABCMeta


class NotFound(Exception, metaclass=ABCMeta):
    pass
