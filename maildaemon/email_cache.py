
import abc
import typing as t

from .message import Message


class EmailCache(metaclass=abc.ABCMeta):
    """An object that stores e-mail messages."""

    def __init__(self):
        self.folders = []  # type: t.List[str]
        self.message_ids = {}  # type: t.Mapping[str, t.List[int]]
        self.messages = {}  # type: t.Mapping[t.Tuple[str, int], Message]

    @abc.abstractmethod
    def update_folders(self):
        pass

    @abc.abstractmethod
    def retrieve_messages(
            self, message_ids: t.List[int], folder: t.Optional[str] = None) -> t.List[Message]:
        pass

    @abc.abstractmethod
    def retrieve_message(self, message_id: int, folder: t.Optional[str] = None) -> Message:
        pass

    @abc.abstractmethod
    def update_messages(self):
        pass

    def update(self):
        self.update_folders()
        self.update_messages()
