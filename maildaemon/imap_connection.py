"""IMAP connection handling."""

import datetime
import imaplib
import json
import logging
import pathlib
import shlex
import socket
import typing as t

import colorama
from requests_oauthlib import OAuth2Session
import timing

from .connection import Response, Connection

_LOG = logging.getLogger(__name__)
_TIME = timing.get_timing_group(__name__)

TIMEOUT = 10

socket.setdefaulttimeout(TIMEOUT)


class IMAPConnection(Connection):
    """For handling IMAP connections.

    According to imaplib.IMAP4 documentation: "All IMAP4rev1 commands are supported".
    IMAP version 4 revision 1: https://tools.ietf.org/html/rfc3501

    This class aims at simplyfing usage of those IMAP commands but also
    at (at least partial) error handling and recovery from errors whenever possible.
    """

    ports = [143]
    ssl_ports = [993]

    def __init__(self, domain: str, port: t.Optional[int] = None, ssl: bool = True,
                 oauth: bool = False):
        super().__init__(domain, port, ssl, oauth)

        if self.ssl:
            self._link = imaplib.IMAP4_SSL(self.domain, self.port)
        else:
            self._link = imaplib.IMAP4(self.domain, self.port)
        # self._link.debug = 4

        self._folder = None  # type: str

    def connect(self) -> None:
        """Use imaplib.login() command."""
        status = None
        try:
            if self.oauth:
                status, response = self._connect_oauth()
            else:
                status, response = self._link.login(self.login, self.password)
            _LOG.info('%s%s%s: login(%s, %s) status: %s, response: %s%s%s',
                      colorama.Style.DIM, self, colorama.Style.RESET_ALL,
                      self.login, '***', status,
                      colorama.Style.DIM, Response(response), colorama.Style.RESET_ALL)
        except imaplib.IMAP4.error as err:
            _LOG.exception('%s: login(%s, %s) failed', self, self.login, '***')
            raise RuntimeError('connect() failed') from err

        if status != 'OK':
            raise RuntimeError('connect() failed')

        _LOG.debug('%s%s%s: capabilities: %s', colorama.Style.DIM, self, colorama.Style.RESET_ALL,
                   self._link.capabilities)

    def _connect_oauth(self) -> tuple:
        token_path = pathlib.Path(f'token_{self._login.replace("@", "_")}.json')

        token_valid = False
        if token_path.is_file():
            with token_path.open() as token_file:
                token = json.load(token_file)

            expiration_time = datetime.datetime.fromtimestamp(token['expires_at'])
            if datetime.datetime.now() + datetime.timedelta(seconds=60 * 30) < expiration_time:
                token_valid = True
                _LOG.info('OAUTH token will expire on %s', expiration_time)
            else:
                _LOG.warning('OAUTH token will expire on %s', expiration_time)
                oauth = OAuth2Session(self.oauth_data['client_id'], token=token)
                # token['refresh_token'] is used below
                token = oauth.refresh_token(
                    self.oauth_data['token_uri'], client_id=self.oauth_data['client_id'],
                    client_secret=self.oauth_data['client_secret'])
                with token_path.open('w') as token_file:
                    json.dump(token, token_file)
                token_valid = True

        if not token_valid:
            oauth = OAuth2Session(
                self.oauth_data['client_id'], redirect_uri='https://localhost/',
                scope=self.oauth_data['scopes'])
            authorization_url, state = oauth.authorization_url(
                self.oauth_data['auth_uri'], **self.oauth_data['auth_uri_params'])
            print(f'state: {state}')
            print(f'Please go to {authorization_url} and authorize access for {self.login}.')
            authorization_response = input('Enter the full callback URL: ')
            token = oauth.fetch_token(
                self.oauth_data['token_uri'],
                authorization_response=authorization_response,
                client_secret=self.oauth_data['client_secret'])
            with token_path.open('w') as token_file:
                json.dump(token, token_file)

        with token_path.open() as token_file:
            token = json.load(token_file)
        auth_string = f'''user={self._login}\1auth=Bearer {token['access_token']}\1\1'''

        def auth_handler(response: bytes):
            _LOG.debug('auth_handler got: %s', Response(response))
            if not response:
                _LOG.debug('auth_handler returning: %s', auth_string)
                return auth_string.encode()
            return ''

        return self._link.authenticate('XOAUTH2', auth_handler)

    def is_alive(self) -> bool:
        """Use imaplib.noop() command."""
        status = None
        try:
            status, response = self._link.noop()
            _LOG.info(
                '%s%s%s: noop() status: %s, response: %s%s%s',
                colorama.Style.DIM, self, colorama.Style.RESET_ALL,
                status, colorama.Style.DIM, Response(response), colorama.Style.RESET_ALL)
        except imaplib.IMAP4.error as err:
            _LOG.warning('%s: noop() failed due to %s: %s', self, type(err).__name__, err)
            # raise RuntimeError('is_alive() failed') from err
        except OSError as err:
            _LOG.warning('%s: noop() failed due to %s: %s', self, type(err).__name__, err)
            # raise RuntimeError('is_alive() failed') from err

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

    def retrieve_folders_with_flags(self) -> t.List[t.Tuple[str, t.Set[str]]]:
        """Use imaplib.list() command."""
        status = None
        try:
            status, raw_folders = self._link.list()
            folders = [r.decode() for r in raw_folders]
            _LOG.info('%s%s%s: list() status: %s, folders: %s%s%s',
                      colorama.Style.DIM, self, colorama.Style.RESET_ALL,
                      status, colorama.Style.DIM, folders, colorama.Style.RESET_ALL)
        except imaplib.IMAP4.error as err:
            _LOG.exception('%s: list() failed', self)
            raise RuntimeError('retrieve_folders() failed') from err

        if status != 'OK':
            raise RuntimeError('retrieve_folders() failed')

        folders_with_flags = []
        for folder in folders:
            # end = folder.rfind('"')
            # begin = folder.rfind('"', 1, end) + 1
            # folders[i] = folder[begin:end]
            *raw_flags, _, folder_name = shlex.split(folder)
            flag_str = raw_flags if isinstance(raw_flags, str) else ' '.join(raw_flags)
            flag_str = flag_str[1:-1]
            flags = set(flag_str.split())
            if flags:
                _LOG.debug('%s%s%s: folder "%s" has flags %s',
                           colorama.Style.DIM, self, colorama.Style.RESET_ALL, folder_name, flags)
            folders_with_flags.append((folder_name, flags))

        return folders_with_flags

    def retrieve_folders(self) -> t.List[str]:
        """Get list of IMAP folders."""
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

    def open_folder(self, folder: t.Optional[str] = None) -> None:
        """Open an IMAP folder.

        :param folder: optional, opens default folder if none provided

        Use imaplib.fetch() command.
        """
        if folder is None:
            folder = 'INBOX'

        if self._folder == folder:
            return

        status = None
        try:
            status, response = self._link.select(f'"{folder}"')
            _LOG.info('%s%s%s: select("%s") status: %s, response: %s%s%s',
                      colorama.Style.DIM, self, colorama.Style.RESET_ALL, folder,
                      status, colorama.Style.DIM, Response(response), colorama.Style.RESET_ALL)
        except imaplib.IMAP4.error as err:
            _LOG.exception('%s: select("%s") failed', self, folder)
            raise RuntimeError('open_folder() failed') from err

        if status != 'OK':
            raise RuntimeError('open_folder() failed')

        self._folder = folder

    def retrieve_message_ids(self, folder: t.Optional[str] = None) -> t.List[int]:
        """Use imaplib.search() command."""
        if folder is None:
            folder = self._folder

        self.open_folder(folder)

        status = None
        try:
            with _TIME.measure('retrieve_message_ids') as timer:
                status, response = self._link.uid('search', None, 'ALL')
            _LOG.info(
                '%s%s%s: search(%s, %s) completed in %fs status: %s, response: %s%s%s',
                colorama.Style.DIM, self, colorama.Style.RESET_ALL, None, 'ALL', timer.elapsed,
                status, colorama.Style.DIM, Response(response), colorama.Style.RESET_ALL)
        except imaplib.IMAP4.error as err:
            _LOG.exception('%s: search(%s, %s) failed', self, None, 'ALL')
            raise RuntimeError('retrieve_message_ids() failed') from err

        if status != 'OK':
            raise RuntimeError('retrieve_message_ids() failed')

        message_ids = [int(message_id) for message_id in response[0].decode().split()]

        return message_ids

    def retrieve_messages_parts(
            self, message_ids: t.List[int], parts: t.List[str],
            folder: t.Optional[str] = None) -> t.List[t.Tuple[bytes, t.Optional[bytes]]]:
        """Retrieve message parts for requested list of messages.

        :param message_ids: list of message identifiers
        :param parts: list of one or more of the following parts defined in the standard:
          'UID', 'ENVELOPE', 'FLAGS', 'RFC822', 'BODY', 'BODY.PEEK[HEADER]', 'BODY.PEEK[]', etc.
        :param folder: optional, uses currently open folder if none provided, and opens default
          folder if none is opened

        Use imaplib.fetch() command.

        Return list of tuples. One tuple (envelope, body) for each requested message id. Contents
        of both tuple elements depend on requested message parts, and body element might be None.
        """
        assert message_ids
        assert parts

        if folder is None:
            folder = self._folder

        self.open_folder(folder)

        status = None
        try:
            with _TIME.measure('retrieve_messages_parts') as timer:
                status, messages_data = self._link.uid(
                    'fetch', ','.join([str(message_id) for message_id in message_ids]),
                    '({})'.format(' '.join(parts)))
            _LOG.info(
                '%s%s%s: fetch(%s, %s) completed in %fs status: %s, len(messages_data): %i',
                colorama.Style.DIM, self, colorama.Style.RESET_ALL, message_ids, parts,
                timer.elapsed, status, len(messages_data))
            # _LOG.debug('data: %s', data) # large output
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
            for i in range(len(messages_data) - 1, -1, -2):
                messages_data[i - 1] = (messages_data[i - 1][0] + messages_data[i][0],
                                        messages_data[i - 1][1])
                del messages_data[i]

        return messages_data

    def retrieve_message_parts(
            self, message_id: int, parts: t.List[str],
            folder: t.Optional[str] = None) -> t.Tuple[bytes, t.Optional[bytes]]:
        """Retrieve message parts for requested message.

        :param message_id: single message identifier
        :param parts: list of one or more of the following parts defined in the standard:
          'UID', 'ENVELOPE', 'FLAGS', 'RFC822', 'BODY', 'BODY.PEEK[HEADER]', 'BODY.PEEK[]', etc.
        :param folder: optional, uses currently open folder if none provided, and opens default
          folder if none is opened

        Return a single tuple (envelope, body). Contents of both tuple elements depend on requested
        message parts, and body element might be None.
        """
        data = self.retrieve_messages_parts([message_id], parts, folder)
        return data[0]

    def _alter_messages_flags(
            self, message_ids: t.Sequence[int], flags: t.Sequence[str],
            alteration: t.Optional[bool], silent: bool = False,
            folder: t.Optional[str] = None) -> None:
        """Alter flags on messages.

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

        command = f'{command_prefix}FLAGS{command_suffix}'

        status = None
        try:
            status, response = self._link.uid(
                'store', ','.join([str(message_id) for message_id in message_ids]), command,
                '({})'.format(' '.join(['\\{}'.format(flag) for flag in flags])))
            _LOG.info(
                '%s%s%s: store(%s, %s, %s) status: %s, response: %s',
                colorama.Style.DIM, self, colorama.Style.RESET_ALL, message_ids, command, flags,
                status, response)
        except imaplib.IMAP4.error as err:
            _LOG.exception('%s: store(%s, "%s", %s) failed', self, message_ids, command, flags)
            raise RuntimeError('alter_messages_flags() failed') from err

        if status != 'OK':
            raise RuntimeError('alter_messages_flags() failed')

    def add_messages_flags(
            self, message_ids: t.List[int], flags: t.Sequence[str], silent: bool = False,
            folder: t.Optional[str] = None):
        """Issue "+FLAGS" command."""
        self._alter_messages_flags(message_ids, flags, True, silent, folder)

    def remove_messages_flags(
            self, message_ids: t.List[int], flags: t.Sequence[str], silent: bool = False,
            folder: t.Optional[str] = None):
        """Issue "-FLAGS" command."""
        self._alter_messages_flags(message_ids, flags, False, silent, folder)

    def set_messages_flags(
            self, message_ids: t.List[int], flags: t.Sequence[str], silent: bool = False,
            folder: t.Optional[str] = None):
        """Issue "FLAGS" command."""
        self._alter_messages_flags(message_ids, flags, None, silent, folder)

    def add_messages(self, messages_parts: t.List[t.Tuple[bytes, bytes]],
                     folder: t.Optional[str] = None) -> None:
        for message_parts in messages_parts:
            self.add_message(message_parts, folder)

    def add_message(self, message_parts: t.Tuple[bytes, bytes],
                    folder: t.Optional[str] = None) -> None:
        """Add a message to a folder using APPEND command.

        :param message_parts: tuple (envelope: bytes, body: bytes), with both elements properly set,
          which is exactly the same type as received via:
          parts = retrieve_message_parts(uid, parts=['FLAGS', 'INTERNALDATE', 'BODY.PEEK[]'])
        """
        assert isinstance(message_parts, tuple), type(message_parts)
        assert len(message_parts) == 2, len(message_parts)
        envelope, body = message_parts
        assert isinstance(envelope, bytes), type(envelope)
        assert isinstance(body, bytes), type(body)

        if folder is None:
            folder = self._folder
        self.open_folder(folder)

        flags = f'({" ".join(_.decode() for _ in imaplib.ParseFlags(envelope))})'
        assert isinstance(flags, str), flags
        date = imaplib.Time2Internaldate(imaplib.Internaldate2tuple(envelope))
        assert date is not None

        status = None
        try:
            status, response = self._link.append(folder, flags, date, body)
            _LOG.info('%s%s%s: append("%s", %s, "%s", ... (%i bytes)) status: %s, response: %s',
                      colorama.Style.DIM, self, colorama.Style.RESET_ALL, folder, flags, date,
                      len(body), status, [r for r in response])
        except imaplib.IMAP4.error as err:
            _LOG.exception('%s: append("%s", %s, "%s", ... (%i bytes)) failed',
                           self, folder, flags, date, len(body))
            raise RuntimeError('add_message() failed') from err

        if status != 'OK':
            raise RuntimeError('add_message() failed')

    def copy_messages(
            self, message_ids: t.List[int], target_folder: str,
            source_folder: t.Optional[str] = None) -> None:
        """Copy messages to a different folder within the same connection."""
        if source_folder is None:
            source_folder = self._folder

        self.open_folder(source_folder)

        if self._folder == target_folder:
            raise RuntimeError(
                'copy_messages() failed because source and target folders are the same')

        status = None
        try:
            status, response = self._link.uid(
                'copy', ','.join([str(message_id) for message_id in message_ids]),
                f'"{target_folder}"')
            _LOG.info(
                '%s%s%s: copy(%s, "%s") status: %s, response: %s%s%s',
                colorama.Style.DIM, self, colorama.Style.RESET_ALL, message_ids, target_folder,
                status, colorama.Style.DIM, Response(response), colorama.Style.RESET_ALL)
        except imaplib.IMAP4.error as err:
            _LOG.exception('%s: copy(%s, "%s") failed', self, message_ids, target_folder)
            raise RuntimeError('copy_messages() failed') from err

        if status != 'OK':
            raise RuntimeError('copy_messages() failed')

    def copy_message(
            self, message_id: int, target_folder: str,
            source_folder: t.Optional[str] = None) -> None:
        self.copy_messages([message_id], target_folder, source_folder)

    def delete_messages(self, message_ids: t.List[int], folder: t.Optional[str] = None,
                        purge_immediately: bool = False) -> None:
        self.add_messages_flags(message_ids, ['Deleted'], folder=folder)
        if purge_immediately:
            self.purge_deleted_messages(folder=folder)

    def delete_message(self, message_id: int, folder: t.Optional[str] = None,
                       purge_immediately: bool = False) -> None:
        self.delete_messages([message_id], folder, purge_immediately)

    def purge_deleted_messages(self, folder: t.Optional[str] = None) -> None:
        """Use imaplib.expunge()."""
        if folder is None:
            folder = self._folder
        self.open_folder(folder)
        status = None
        try:
            status, response = self._link.expunge()
            _LOG.info('%s: expunge() status: %s, response: %s',
                      self, status, [r for r in response])
        except imaplib.IMAP4.error as err:
            _LOG.exception('%s: expunge() failed', self)
            raise RuntimeError('purge_deleted_messages() failed') from err

        if status != 'OK':
            raise RuntimeError('purge_deleted_messages() failed')

    def move_messages(
            self, message_ids: t.List[int], target_folder: str,
            source_folder: t.Optional[str] = None) -> None:
        """Move messages from one folder to a different folder on the same connection.

        This method does not rely on MOVE command https://tools.ietf.org/html/rfc6851
        """
        self.copy_messages(message_ids, target_folder, source_folder)
        self.delete_messages(message_ids, source_folder)

    def move_message(self, message_id: int, target_folder: str,
                     source_folder: t.Optional[str] = None) -> None:
        self.move_messages([message_id], target_folder, source_folder)

    def close_folder(self) -> None:
        """Use imaplib.close() command."""
        if self._folder is None:
            return

        status = None
        try:
            status, response = self._link.close()
            _LOG.info('%s%s%s: close() status: %s, response: %s%s%s',
                      colorama.Style.DIM, self, colorama.Style.RESET_ALL,
                      status, colorama.Style.DIM, Response(response), colorama.Style.RESET_ALL)
        except imaplib.IMAP4.error as err:
            _LOG.exception('%s: close() failed', self)
            raise RuntimeError('close_folder() failed') from err

        if status != 'OK':
            raise RuntimeError('close_folder() failed')

        self._folder = None

    def disconnect(self) -> None:
        """Use imaplib.logout() command."""
        self.close_folder()

        status = None
        try:
            status, response = self._link.logout()
            _LOG.info('%s%s%s: logout() status: %s, response: %s%s%s',
                      colorama.Style.DIM, self, colorama.Style.RESET_ALL,
                      status, colorama.Style.DIM, Response(response), colorama.Style.RESET_ALL)
        except imaplib.IMAP4.error as err:
            _LOG.exception('%s: logout() failed', self)
            raise RuntimeError('disconnect() failed') from err

        if status != 'BYE':
            raise RuntimeError('disconnect() failed')
