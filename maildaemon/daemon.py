
import abc


class Daemon(metaclass=abc.ABCMeta):
    """Daemon interface."""

    def __init__(self):
        pass

    @abc.abstractmethod
    def update(self):
        pass

    # @abc.abstractmethod
    def run(self):
        pass
