"""Cache for messages accessed via POP connections."""

import email.parser
import logging
import typing as t

from .message import Message
from .folder import Folder
from .email_cache import EmailCache
from .pop_connection import POPConnection

_LOG = logging.getLogger(__name__)


class POPCache(EmailCache, POPConnection):
    """Cache for messages accessed via POP connections."""

    def __init__(self, domain: str, port: t.Optional[int] = None, ssl: bool = True):
        EmailCache.__init__(self)
        POPConnection.__init__(self, domain, port, ssl)
        # self.folders = ['INBOX']  # type: t.List[str]
        # self.message_ids = {'INBOX': []}  # type: t.Mapping[str, t.List[int]]
        # self.messages = {}  # type: t.Mapping[t.Tuple[str, int], Message]

    def update_folders(self):
        if not self.folders:
            self.folders['INBOX'] = Folder(self, 'INBOX')
        assert len(self.folders) == 1, len(self.folders)
        assert 'INBOX' in self.folders, self.folders

    def retrieve_messages(self, message_ids: t.List[int]) -> t.List[Message]:
        messages = []
        for message_id in message_ids:
            message = self.retrieve_message(message_id)
            messages.append(message)
        return messages

    def retrieve_message(self, message_id: int) -> Message:
        message_lines = self.retrieve_message_lines(message_id)

        bytes_feed_parser = email.parser.BytesFeedParser()
        for message_line in message_lines:
            bytes_feed_parser.feed(message_line + b'\n')
        email_message = bytes_feed_parser.close()

        if email_message.defects:
            for defect in email_message.defects:
                _LOG.error('%s: message #%i has defect: %s', self, message_id, defect)

        return Message(email_message, self, None, message_id)

    def update_messages_in(self, folder: Folder):
        assert folder.name == 'INBOX', folder

        message_ids = self.retrieve_message_ids()
        # new_message_ids = []

        # for message_id in self.message_ids['INBOX']:
        #     if message_id not in message_ids:
        #         _LOG.warning('%s: message #%i was deleted', self, message_id)
        #         self.message_ids['INBOX'].remove(message_id)
        #         del self.messages['INBOX', message_id]

        # for message_id in message_ids:
        #     if message_id not in self.message_ids['INBOX']:
        #         _LOG.info('%s: new message #%i found', self, message_id)
        #         self.message_ids['INBOX'].append(message_id)
        #         new_message_ids.append(message_id)

        # new_messages = self.retrieve_messages(new_message_ids)

        messages = self.retrieve_messages(message_ids)
        for message in messages:
            folder.add_message(message)

        # for new_message_id, new_message in zip(new_message_ids, new_messages):
        #     if ('INBOX', new_message_id) in self.messages:
        #         _LOG.error('%s: message #%i is not really new\ncurrent:\n%s\nnew:\n%s',
        #                    self, new_message_id, repr(self.messages['INBOX', new_message_id]),
        #                    repr(new_message))
        #     self.messages['INBOX', new_message_id] = new_message
