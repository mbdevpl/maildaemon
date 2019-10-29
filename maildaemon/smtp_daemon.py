"""Daemon working with SMTP connections."""

import email.message
import typing as t

from .message import Message
from .daemon import Daemon
from .smtp_connection import SMTPConnection


class SMTPDaemon(Daemon, SMTPConnection):
    """Daemon working with SMTP connections."""

    def __init__(self, domain: str, port: t.Optional[int] = None, ssl: bool = True):
        Daemon.__init__(self)
        SMTPConnection.__init__(self, domain, port, ssl)

        self._outbox = []

    @property
    def outbox(self):
        return self._outbox

    def add_to_outbox(self, message: t.Union[Message, email.message.Message]) -> None:
        self._outbox.append(message)

    def send_message(self, message: t.Union[Message, email.message.Message]) -> None:
        if isinstance(message, email.message.Message):
            super().send_message(message)
            return
        message.send_via(self)

    def update(self):
        if not self._outbox:
            return
        for message in self._outbox:
            self.send_message(message)
        self._outbox.clear()
