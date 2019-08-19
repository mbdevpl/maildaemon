"""Abstract class defining cache of e-mail messages."""

import abc
import typing as t

from .message import Message
from .folder import Folder


class EmailCache(metaclass=abc.ABCMeta):
    """An object that stores e-mail messages."""

    def __init__(self):
        self.folders = {}  # type: t.Dict[str, Folder]
        # self.message_ids = {}  # type: t.Mapping[str, t.List[int]]
        # self.messages = {}  # type: t.Mapping[t.Tuple[str, int], Message]

    @abc.abstractmethod
    def update_folders(self):
        """Rebuild the folders dictionary."""
        ...

    # @abc.abstractmethod
    # def retrieve_messages(
    #         self, message_ids: t.List[int], folder: t.Optional[str] = None) -> t.List[Message]:
    #     pass
    #
    # @abc.abstractmethod
    # def retrieve_message(self, message_id: int, folder: t.Optional[str] = None) -> Message:
    #     pass

    def update_messages(self):
        for _, folder in self.folders.items():
            self.update_messages_in(folder)

    @abc.abstractmethod
    def update_messages_in(self, folder: Folder):
        """Update messages stored in a given folder."""
        ...

    def update(self):
        self.update_folders()
        self.update_messages()
