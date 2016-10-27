
import imaplib
import logging
import typing as t

from .connection import Connection

_LOG = logging.getLogger(__name__)

class IMAPConnection(Connection):
    """
    For handling IMAP connections.

    According to imaplib.IMAP4 documentation: "All IMAP4rev1 commands are supported".

    IMAP version 4 revision 1: https://tools.ietf.org/html/rfc3501
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

        try:
            status, response = self._link.login(self.login, self.password)
            _LOG.info(
                '%s: login(%s, %s) status: %s, response: %s',
                self, self.login, '***', status, [r.decode() for r in response])
            if status != 'OK':
                raise RuntimeError('connect() failed')
        except imaplib.IMAP4.error as err:
            _LOG.exception('%s: login(%s, %s) failed', self, self.login, '***')
            raise RuntimeError('connect() failed') from err

    def is_alive(self) -> bool:
        """
        Use imaplib.noop() command.
        """

        is_alive = False

        try:
            status, response = self._link.noop()
            _LOG.info(
                '%s: noop() status: %s, response: %s', self, status, [r.decode() for r in response])
            is_alive = status == 'OK'
        except imaplib.IMAP4.error as err:
            _LOG.exception('%s: noop() failed', self)
            raise RuntimeError('is_alive() failed') from err
        except OSError as err:
            _LOG.exception('%s: noop() failed', self)
            raise RuntimeError('is_alive() failed') from err

        return is_alive

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

    def retrieve_folders(self) -> t.List[str]:
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

        for i, folder in enumerate(folders):
            end = folder.rfind('"')
            begin = folder.rfind('"', 1, end) + 1
            folders[i] = folder[begin:end]

        return folders

    '''
    def create_folder(self, folder: str) -> None:

        raise NotImplementedError()

    def delete_folder(self, folder: str) -> None:

        raise NotImplementedError()
    '''

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

        self.select_folder(folder)

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
