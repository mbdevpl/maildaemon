"""

"""

import email
import logging
import typing as t

from .message import Message
from .daemon import Daemon
from .imap_connection import IMAPConnection

_LOG = logging.getLogger(__name__)

class IMAPDaemon(Daemon, IMAPConnection):

    def __init__(self, domain: str, ssl: bool=True, port: t.Optional[int]=None):
        Daemon.__init__(self)
        IMAPConnection.__init__(self, domain, ssl, port)

        self.folders = [] # type: t.List[str]
        self.message_ids = {} # type: t.Mapping[str, t.List[int]]
        self.messages = {} # type: t.Mapping[t.Tuple[str, int], Message]

    def update_folders(self):

        folders = self.retrieve_folders()

        for folder in self.folders:
            if folder not in folders:
                _LOG.warning('%s: folder "%s" was deleted', self, folder)
                self.folders.remove(folder)
                for message_id in self.message_ids[folder]:
                    del self.messages[folder, message_id]
                del self.message_ids[folder]

        for folder in folders:
            if folder not in self.folders:
                _LOG.info('%s: new folder "%s" found', self, folder)
                self.folders.append(folder)

    def retrieve_messages(
            self, message_ids: t.List[int], folder: t.Optional[str]=None) -> t.List[Message]:
        """
        For each message identifier request BODY.PEEK[] message part and parse it to Message.

        The BODY.PEEK[] is a functional equivalent of obsolete RFC822.PEEK,
        see https://www.ietf.org/rfc/rfc2062 for details.
        """

        messages_data = self.retrieve_messages_parts(message_ids, ['BODY.PEEK[]'], folder)

        messages = []
        for message_id, (_, body) in zip(message_ids, messages_data):
            email_message = email.message_from_bytes(body)
            if email_message.defects:
                for defect in email_message.defects:
                    _LOG.error(
                        '%s: message #%i in "%s" has defect: %s',
                        self, message_id, self._folder, defect)

            message = Message.from_email_message(email_message)
            messages.append(message)

        return messages

    def retrieve_message(self, message_id: int, folder: t.Optional[str]=None) -> Message:

        messages = self.retrieve_messages([message_id], folder)

        return messages[0]

    def _update_messages_in(self, folder: str):

        message_ids = self.retrieve_message_ids(folder)
        new_message_ids = []

        folder = self._folder

        if folder in self.message_ids:

            for message_id in self.message_ids[folder]:
                if message_id not in message_ids:
                    _LOG.warning('%s: message #%i in folder "%s" was deleted', self, message_id, folder)
                    self.message_ids[folder].remove(message_id)
                    del self.messages[folder, message_id]
                    #try:
                    #except KeyError:
                    #    _LOG.exception('%s: deleted a non-existing message "%i" from folder "%s"', self, message_id, folder)

            for message_id in message_ids:
                if message_id not in self.message_ids[folder]:
                    _LOG.info('%s: new message #%i in folder "%s" found', self, message_id, folder)
                    self.message_ids[folder].append(message_id)
                    new_message_ids.append(message_id)

        else:
            _LOG.info('%s: %i messages found in new folder "%s"', self, len(message_ids), folder)
            self.message_ids[folder] = message_ids
            new_message_ids = message_ids

        if len(new_message_ids) == 0:
            return

        new_messages = self.retrieve_messages(new_message_ids, folder)

        for new_message_id, new_message in zip(new_message_ids, new_messages):
            if (folder, new_message_id) in self.messages:
                _LOG.error(
                    '%s: message #%i from folder "%s" is not really new\ncurrent:\n%s\nnew:\n%s',
                    self, new_message_id, folder, repr(self.messages[folder, new_message_id]),
                    repr(new_message))
            self.messages[folder, new_message_id] = new_message

    def update(self):

        self.update_folders()

        for folder in self.folders:
            try:
                self.open_folder(folder)
            except RuntimeError:
                _LOG.warning('%s: skipping folder "%s"', self, folder)
                continue
            self._update_messages_in(folder)
            self.close_folder()
