"""E-mail cache working with IMAP connections."""

import email
import imaplib
import logging
import typing as t

import colorama

from .message import Message
from .folder import Folder
from .email_cache import EmailCache
from .imap_connection import IMAPConnection

_LOG = logging.getLogger(__name__)

HEADER_ONLY_IGNORED_DEFECTS = (
    email.errors.StartBoundaryNotFoundDefect, email.errors.MultipartInvariantViolationDefect)


class IMAPCache(EmailCache, IMAPConnection):
    """E-mail cache working with IMAP connections."""

    def __init__(self, domain: str, port: t.Optional[int] = None, ssl: bool = True,
                 oauth: bool = False):
        EmailCache.__init__(self)
        IMAPConnection.__init__(self, domain, port, ssl, oauth)

    def update_folders(self):
        folders = dict(self.retrieve_folders_with_flags())

        for name, folder in self.folders.items():
            if name not in folders:
                _LOG.warning('%s: folder %s was deleted', self, folder)
                del self.folders[name]
            elif folder.flags ^ folders[name]:
                _LOG.warning('%s: folder %s flags changed into %s', self, folder, folders[name])
                folder._flags = folders[name]

        for folder_name, flags in folders.items():
            if folder_name not in self.folders:
                _LOG.info('%s%s%s: new folder "%s" found',
                          colorama.Style.DIM, self, colorama.Style.RESET_ALL, folder_name)
                self.folders[folder_name] = Folder(self, folder_name, flags)

    def update_messages_in(self, folder: Folder):
        if folder.name != 'INBOX':
            return  # TODO: in the future, fetch all folders
        try:
            self.open_folder(folder.name)
        except RuntimeError:
            _LOG.exception('%s: skipping folder "%s"', self, folder)
            return

        assert folder.name == self._folder, (self._folder)
        message_ids = self.retrieve_message_ids(folder.name)
        messages = self.retrieve_messages(message_ids, folder.name, headers_only=True)

        folder._messages = messages

        # for message_id in self.message_ids[folder]:
        #     if message_id not in message_ids:
        #         _LOG.warning('%s: message #%i in folder "%s" was deleted',
        #                      self, message_id, folder)
        #         self.message_ids[folder].remove(message_id)
        #         del self.messages[folder, message_id]
        #         # try:
        #         # except KeyError:
        #         #    LOG.exception('%s: deleted a non-existing message "%i" from folder "%s"',
        #         #                  self, message_id, folder)
        #
        # for message_id in message_ids:
        #     if message_id not in self.message_ids[folder]:
        #         _LOG.info('%s: new message #%i in folder "%s" found', self, message_id, folder)
        #         self.message_ids[folder].append(message_id)
        #         new_message_ids.append(message_id)

        # else:
        #     _LOG.info('%s: %i messages found in new folder "%s"', self, len(message_ids), folder)
        #     self.message_ids[folder] = message_ids
        #     new_message_ids = message_ids

        # self._update_messages_in(folder.name)

        self.close_folder()

    '''
    def _update_messages_in(self, folder: str):

        message_ids = self.retrieve_message_ids(folder)
        new_message_ids = []

        folder = self._folder

        if folder in self.message_ids:

            for message_id in self.message_ids[folder]:
                if message_id not in message_ids:
                    _LOG.warning('%s: message #%i in folder "%s" was deleted',
                                 self, message_id, folder)
                    self.message_ids[folder].remove(message_id)
                    del self.messages[folder, message_id]
                    # try:
                    # except KeyError:
                    #    LOG.exception('%s: deleted a non-existing message "%i" from folder "%s"',
                    #                  self, message_id, folder)

            for message_id in message_ids:
                if message_id not in self.message_ids[folder]:
                    _LOG.info('%s: new message #%i in folder "%s" found', self, message_id, folder)
                    self.message_ids[folder].append(message_id)
                    new_message_ids.append(message_id)

        else:
            _LOG.info('%s: %i messages found in new folder "%s"', self, len(message_ids), folder)
            self.message_ids[folder] = message_ids
            new_message_ids = message_ids

        if not new_message_ids:
            return

        new_messages = self.retrieve_messages(new_message_ids, folder)

        for new_message_id, new_message in zip(new_message_ids, new_messages):
            if (folder, new_message_id) in self.messages:
                _LOG.error(
                    '%s: message #%i from folder "%s" is not really new\ncurrent:\n%s\nnew:\n%s',
                    self, new_message_id, folder, repr(self.messages[folder, new_message_id]),
                    repr(new_message))
            self.messages[folder, new_message_id] = new_message
    '''

    def retrieve_messages(
            self, message_ids: t.List[int], folder: t.Optional[str] = None,
            headers_only: bool = False) -> t.List[Message]:
        """For each message ID request message flags and contents and parse it to Message."""

        requested_parts = ['FLAGS']
        # The BODY.PEEK[] is a functional equivalent of obsolete RFC822.PEEK,
        # see https://www.ietf.org/rfc/rfc2062 for details.
        requested_parts.append('BODY.PEEK[HEADER]' if headers_only else 'BODY.PEEK[]')

        # flags_data = self.retrieve_messages_parts(message_ids, ['FLAGS'], folder)
        # print(flags_data[0])
        # all_data = self.retrieve_messages_parts(message_ids, ['FLAGS', 'BODY.PEEK[]'], folder)
        # print(all_data[0])
        messages_data = self.retrieve_messages_parts(message_ids, requested_parts, folder)

        messages = []
        for message_id, (metadata, message) in zip(message_ids, messages_data):
            email_message = email.message_from_bytes(message)
            if headers_only:
                email_message.defects = [
                    defect for defect in email_message.defects
                    if not isinstance(defect, HEADER_ONLY_IGNORED_DEFECTS)]
            if email_message.defects:
                _LOG.error('%s: message #%i in "%s" has defects: %s',
                           self, message_id, self._folder, email_message.defects)

            message = Message(email_message, self, self._folder, message_id)
            flags = imaplib.ParseFlags(metadata)
            for raw_flag in flags:
                flag = raw_flag.decode()
                if flag.startswith('\\'):
                    flag = flag[1:]
                else:
                    _LOG.warning('atypical flag "%s" detected in "%s"', flag, flags)
                message.flags.add(flag)
            messages.append(message)

        return messages

    def retrieve_message(self, message_id: int, folder: t.Optional[str] = None) -> Message:
        messages = self.retrieve_messages([message_id], folder)
        return messages[0]
