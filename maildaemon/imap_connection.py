
import imaplib
import logging
import shlex
import socket
import typing as t

from .connection import Connection

_LOG = logging.getLogger(__name__)

TIMEOUT = 10

socket.setdefaulttimeout(TIMEOUT)

class IMAPConnection(Connection):
    """
    For handling IMAP connections.

    According to imaplib.IMAP4 documentation: "All IMAP4rev1 commands are supported".
    IMAP version 4 revision 1: https://tools.ietf.org/html/rfc3501

    This class aims at simplyfing usage of those IMAP commands but also
    at (at least partial) error handling and recovery from errors whenever possible.
    """

    ports = [143]
    ssl_ports = [993]

    def __init__(self, domain: str, ssl: bool=True, port: t.Optional[int]=None):
        super().__init__(domain, ssl, port)

        if self.ssl:
            self._link = imaplib.IMAP4_SSL(self.domain, self.port)
        else:
            self._link = imaplib.IMAP4(self.domain, self.port)

        self._folder = None

    def connect(self) -> None:
        """
        Use imaplib.login() command.
        """

        status = None
        try:
            status, response = self._link.login(self.login, self.password)
            _LOG.info(
                '%s: login(%s, %s) status: %s, response: %s',
                self, self.login, '***', status, [r.decode() for r in response])
        except imaplib.IMAP4.error as err:
            _LOG.exception('%s: login(%s, %s) failed', self, self.login, '***')
            raise RuntimeError('connect() failed') from err

        if status != 'OK':
            raise RuntimeError('connect() failed')

        _LOG.debug('%s: capabilities: %s', self, self._link.capabilities)

    def is_alive(self) -> bool:
        """
        Use imaplib.noop() command.
        """

        status = None
        try:
            status, response = self._link.noop()
            _LOG.info(
                '%s: noop() status: %s, response: %s', self, status, [r.decode() for r in response])
        except imaplib.IMAP4.error as err:
            _LOG.warning('%s: noop() failed due to %s: %s', self, type(err).__name__, err)
            #raise RuntimeError('is_alive() failed') from err
        except OSError as err:
            _LOG.warning('%s: noop() failed due to %s: %s', self, type(err).__name__, err)
            #raise RuntimeError('is_alive() failed') from err

        return status == 'OK'

    '''
    def retrieve_namespace(self):
        """
        Use imaplib.namespace() command.
        """

        status, namespace = self._link.namespace()
        _LOG.debug('namespace() status: %s', status)
        _LOG.debug('namespace: %s', [r.decode() for r in namespace])
        if status != 'OK':
            raise RuntimeError('namespace() status: "{}"'.format(status))
    '''

    def retrieve_folders_with_flags(self) -> t.List[t.Tuple[str, t.List[str]]]:
        """
        Use imaplib.list() command.
        """

        status = None
        try:
            status, raw_folders = self._link.list()
            folders = [r.decode() for r in raw_folders]
            _LOG.info('%s: list() status: %s, folders: %s', self, status, folders)
        except imaplib.IMAP4.error as err:
            _LOG.exception('%s: list() failed', self)
            raise RuntimeError('retrieve_folders() failed') from err

        if status != 'OK':
            raise RuntimeError('retrieve_folders() failed')

        folders_with_flags = []
        for folder in folders:
            #end = folder.rfind('"')
            #begin = folder.rfind('"', 1, end) + 1
            #folders[i] = folder[begin:end]
            *raw_flags, _, folder_name = shlex.split(folder)
            flag_str = raw_flags if isinstance(raw_flags, str) else ' '.join(raw_flags)
            flag_str = flag_str[1:-1]
            flags = flag_str.split()
            _LOG.debug('%s: folder "%s" has flags %s', self, folder_name, flags)
            folders_with_flags.append((folder_name, flags))

        return folders_with_flags

    def retrieve_folders(self) -> t.List[str]:

        folders_with_flags = self.retrieve_folders_with_flags()

        folder_names = []
        for folder_with_flags in folders_with_flags:
            folder_name, _ = folder_with_flags
            folder_names.append(folder_name)

        return folder_names

    def create_folder(self, folder: str) -> None:

        raise NotImplementedError()

    def delete_folder(self, folder: str) -> None:

        raise NotImplementedError()

    def open_folder(self, folder: t.Optional[str]=None) -> None:
        """
        Open an IMAP folder.

        :param folder: optional, opens default folder if none provided

        Use imaplib.fetch() command.
        """

        if folder is None:
            folder = 'INBOX'

        if self._folder == folder:
            return

        status = None
        try:
            status, response = self._link.select('"{}"'.format(folder))
            _LOG.info(
                '%s: select("%s") status: %s, response: %s',
                self, folder, status, [r.decode() for r in response])
        except imaplib.IMAP4.error as err:
            _LOG.exception('%s: select("%s") failed', self, folder)
            raise RuntimeError('open_folder() failed') from err

        if status != 'OK':
            raise RuntimeError('open_folder() failed')

        self._folder = folder

    def retrieve_message_ids(self, folder: t.Optional[str]=None) -> t.List[int]:
        """
        Use imaplib.search() command.
        """

        if folder is None:
            folder = self._folder

        self.open_folder(folder)

        status = None
        try:
            status, response = self._link.search(None, 'ALL')
            _LOG.info(
                '%s: search(%s, %s) status: %s, response: %s',
                self, None, 'ALL', status, [r.decode() for r in response])
        except imaplib.IMAP4.error as err:
            _LOG.exception('%s: search(%s, %s) failed', self, None, 'ALL')
            raise RuntimeError('retrieve_message_ids() failed') from err

        if status != 'OK':
            raise RuntimeError('retrieve_message_ids() failed')

        message_ids = [int(message_id) for message_id in response[0].decode().split()]

        return message_ids

    def retrieve_messages_parts(
            self, message_ids: t.List[int], parts: t.List[str],
            folder: t.Optional[str]=None) -> t.List[t.Tuple[bytes, t.Optional[bytes]]]:
        """
        Retrieve message parts for requested list of messages.

        :param message_ids: list of message identifiers
        :param parts: list of one or more of the following parts defined in the standard:
          'UID', 'ENVELOPE', 'FLAGS', 'RFC822','BODY', 'BODY.PEEK[]', etc.
        :param folder: optional, uses currently open folder if none provided, and opens default
          folder if none is opened

        Use imaplib.fetch() command.

        Return list of tuples. One tuple (envelope, body) for each requested message id. Contents
        of both tuple elements depend on requested message parts, and body element might be None.
        """

        if folder is None:
            folder = self._folder

        self.open_folder(folder)

        status = None
        try:
            status, messages_data = self._link.fetch(
                ','.join([str(message_id) for message_id in message_ids]),
                '({})'.format(' '.join(parts)))
            _LOG.info(
                '%s: fetch(%s, %s) status: %s, len(messages_data): %i',
                self, message_ids, parts, status, len(messages_data))
            #_LOG.debug('data: %s', data) # large output
        except imaplib.IMAP4.error as err:
            _LOG.exception('%s: fetch(%s, %s) failed', self, message_ids, parts)
            raise RuntimeError('retrieve_messages_parts() failed') from err

        if status != 'OK':
            raise RuntimeError('retrieve_messages_parts() failed')

        for i, message_data in enumerate(messages_data):
            if isinstance(message_data, bytes):
                messages_data[i] = (message_data, None)

        if len(messages_data) > len(message_ids):
            assert len(messages_data) == 2 * len(message_ids)
            for i in range(len(messages_data) -1, -1, -2):
                messages_data[i-1] = (messages_data[i-1][0] + messages_data[i][0], messages_data[i-1][1])
                del messages_data[i]

        return messages_data

    def retrieve_message_parts(
            self, message_id: int, parts: t.List[str],
            folder: t.Optional[str]=None) -> t.Tuple[bytes, t.Optional[bytes]]:
        """
        Retrieve message parts for requested message.

        :param message_id: single message identifier
        :param parts: list of one or more of the following parts defined in the standard:
          'UID', 'ENVELOPE', 'FLAGS', 'RFC822','BODY', 'BODY.PEEK[]', etc.
        :param folder: optional, uses currently open folder if none provided, and opens default
          folder if none is opened

        Return a single tuple (envelope, body). Contents of both tuple elements depend on requested
        message parts, and body element might be None.
        """

        data = self.retrieve_messages_parts([message_id], parts, folder)

        return data[0]

    def _alter_messages_flags(
            self, message_ids: t.Sequence[int], flags: t.Sequence[str],
            alteration: t.Optional[bool]=True, silent: bool=False,
            folder: t.Optional[str]=None) -> None:
        """
        Alter flags on messages.

        :param message_ids: list of IDs of messages
        :param flags: list of strings of: 'Deleted', etc.
        :param alteration: True means "+FLAGS", False "-FLAGS" and None means "FLAGS"
        :param silent: add ".SILENT" to the alteration if True
        :param folder: optional, uses currently open folder if none provided, and opens default
          folder if none is opened

        Use imaplib.store().

        See STORE method definition: https://tools.ietf.org/html/rfc3501#section-6.4.6
        """

        if folder is None:
            folder = self._folder

        self.open_folder(folder)

        command_prefix = {True: '+', False: '-', None: ''}[alteration]
        command_suffix = {True: '.SILENT', False: ''}[silent]

        command = '{}FLAGS{}'.format(command_prefix, command_suffix)

        # TODO: add error handling for store()
        status, response = self._link.store(
            ','.join([str(message_id) for message_id in message_ids]), command,
            '({})'.format(' '.join(['\\{}'.format(flag) for flag in flags])))
        _LOG.info(
            '%s: store(%s, %s, %s) status: %s, response: %s',
            self, message_ids, command, flags, status, response)

    def add_messages_flags(
            self, message_ids: t.List[int], flags: t.Sequence[str], silent: bool=False,
            folder: t.Optional[str]=None):
        """
        Issue "+FLAGS" command.
        """

        self._alter_messages_flags(message_ids, flags, True, silent, folder)

    def remove_messages_flags(
            self, message_ids: t.List[int], flags: t.Sequence[str], silent: bool=False,
            folder: t.Optional[str]=None):
        """
        Issue "-FLAGS" command.
        """

        self._alter_messages_flags(message_ids, flags, False, silent, folder)

    def set_messages_flags(
            self, message_ids: t.List[int], flags: t.Sequence[str], silent: bool=False,
            folder: t.Optional[str]=None):
        """
        Issue "FLAGS" command.
        """

        self._alter_messages_flags(message_ids, flags, None, silent, folder)

    def copy_messages(
            self, message_ids: t.List[int], target_folder: str,
            source_folder: t.Optional[str]=None) -> None:
        """
        Copy messages to a different folder within the same connection.
        """

        if source_folder is None:
            source_folder = self._folder

        self.open_folder(source_folder)

        if self._folder == target_folder:
            raise RuntimeError(
                'copy_messages() failed because source and target folders are the same')

        status = None
        try:
            status, response = self._link.copy(
                ','.join([str(message_id) for message_id in message_ids]),
                '"{}"'.format(target_folder))
            _LOG.info(
                '%s: copy(%s, "%s") status: %s, response: %s',
                self, message_ids, target_folder, status, [r.decode() for r in response])
        except imaplib.IMAP4.error as err:
            _LOG.exception('%s: copy(%s, "%s") failed', self, message_ids, target_folder)
            raise RuntimeError('copy_messages() failed') from err

        if status != 'OK':
            raise RuntimeError('copy_messages() failed')

    def copy_message(
            self, message_id: int, target_folder: str,
            source_folder: t.Optional[str]=None) -> None:

        self.copy_messages([message_id], target_folder, source_folder)

    def delete_messages(self, message_ids: t.List[int], folder: t.Optional[str]=None) -> None:

        self.add_messages_flags(message_ids, True, 'Deleted', folder)

    def delete_message(self, message_id: int, folder: t.Optional[str]=None) -> None:

        self.delete_messages([message_id], folder)

    def move_messages(
            self, message_ids: t.List[int], target_folder: str,
            source_folder: t.Optional[str]=None) -> None:
        """
        Move messages from one folder to a different folder on the same connection.

        This method does not rely on MOVE command https://tools.ietf.org/html/rfc6851
        """

        self.copy_messages(message_ids, target_folder, source_folder)
        self.delete_messages(message_ids, source_folder)

    def move_message(
            self, message_id: int, target_folder: str, source_folder: t.Optional[str]=None) -> None:

        self.move_messages([message_id], target_folder, source_folder)

    def close_folder(self) -> None:
        """
        Use imaplib.close() command.
        """

        if self._folder is None:
            return

        status = None
        try:
            status, response = self._link.close()
            _LOG.info(
                '%s: close() status: %s, response: %s',
                self, status, [r.decode() for r in response])
        except imaplib.IMAP4.error as err:
            _LOG.exception('%s: close() failed', self)
            raise RuntimeError('close_folder() failed') from err

        if status != 'OK':
            raise RuntimeError('close_folder() failed')

        self._folder = None

    def disconnect(self) -> None:
        """
        Use imaplib.logout() command.
        """

        self.close_folder()

        status = None
        try:
            status, response = self._link.logout()
            _LOG.info(
                '%s: logout() status: %s, response: %s',
                self, status, [r.decode() for r in response])
        except imaplib.IMAP4.error as err:
            _LOG.exception('%s: logout() failed', self)
            raise RuntimeError('disconnect() failed') from err

        if status != 'BYE':
            raise RuntimeError('disconnect() failed')
