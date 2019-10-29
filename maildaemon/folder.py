"""Folder of e-mail messages."""

import logging
import typing as t

from .connection import Connection
from .message import Message

_LOG = logging.getLogger(__name__)


class Folder:
    """For storing messages."""

    def __init__(self, connection: Connection, name: str, flags: t.Sequence[str] = None):
        if flags is None:
            flags = set()
        self._connection = connection  # type: Connection
        self._name = name  # type: str
        self._flags = set(flags)  # type: t.Set[str]
        self._messages = set()  # type: t.Set[Message]
        self._subfolders = set()  # type: t.Set[Folder]

    @property
    def name(self):
        return self._name

    @property
    def flags(self) -> t.Set[str]:
        return self._flags

    @property
    def messages(self):
        return self._messages

    def add_message(self, message: Message):
        assert isinstance(message, Message)
        assert message not in self._messages
        self._messages.add(message)

    def remove_message(self, message: Message):
        self._messages.remove(message)

    def find_message(self, *args, **kwargs):
        raise NotImplementedError()

    @property
    def subfolders(self):
        return self._subfolders

    def add_subfolder(self, folder):
        assert folder not in self._subfolders
        self._subfolders.add(folder)

    def remove_subfolder(self, folder):
        self._subfolders.remove(folder)
