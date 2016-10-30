'''
Created on Oct 29, 2016

@author: mb
'''

import email.message
import typing as t

from .message import Message
from .daemon import Daemon
from .smtp_connection import SMTPConnection

class SMTPDaemon(Daemon, SMTPConnection):

    def __init__(self, domain: str, ssl: bool=True, port: t.Optional[int]=None):
        Daemon.__init__(self)
        SMTPConnection.__init__(self, domain, ssl, port)

        self._outbox = []

    def add_to_outbox(self, message: Message) -> None:

        self._outbox.append(message)

    def send_message(self, message: t.Union[Message, email.message.Message]) -> None:

        if isinstance(message, email.message.Message):
            super().send_message(message)
            return

        super().send_message(message._email_message)

    def update(self):

        if len(self._outbox) == 0:
            return

        for message in self._outbox:
            self.send_message(message)

        self._outbox.clear()
