"""POP connection handling."""

import logging
import poplib
import typing as t

import colorama

# from .message import Message
from .connection import Connection

_LOG = logging.getLogger(__name__)

TIMEOUT = 10


class POPConnection(Connection):
    """For handling POP connections."""

    ports = [110]
    ssl_ports = [995]

    def __init__(self, domain: str, port: t.Optional[int] = None, ssl: bool = True):
        super().__init__(domain, port, ssl)

        self._link: t.Union[poplib.POP3, poplib.POP3_SSL]
        if self.ssl:
            self._link = poplib.POP3_SSL(self.domain, self.port, timeout=TIMEOUT)
        else:
            self._link = poplib.POP3(self.domain, self.port, timeout=TIMEOUT)

        if not self.ssl:
            self._upgrade_connection()

    def _upgrade_connection(self) -> None:

        if self.ssl:
            return

        status = b''
        try:
            status = self._link.stls()
        except poplib.error_proto:
            _LOG.warning('%s: stls() failed', self)
        else:
            _LOG.info('%s%s%s: stls() status: %s',
                      colorama.Style.DIM, self, colorama.Style.RESET_ALL, status)

        if status.startswith(b'+OK'):
            self.ssl = True
            _LOG.info('%s%s%s: connection upgraded to TLS',
                      colorama.Style.DIM, self, colorama.Style.RESET_ALL)

    def connect(self) -> None:

        if self._connect_secure():
            return

        status = b''
        try:
            status = self._link.user(self.login)
        except poplib.error_proto as err:
            _LOG.exception('%s: list() failed', self)
            raise RuntimeError('retrieve_message_ids() failed') from err
        else:
            _LOG.info('%s%s%s: user(%s) status: %s',
                      colorama.Style.DIM, self, colorama.Style.RESET_ALL, self.login, status)

        if not status.startswith(b'+OK'):
            raise RuntimeError(f'user() status: "{status!r}"')

        status = b''
        try:
            status = self._link.pass_(self.password)
        except poplib.error_proto as err:
            _LOG.exception('%s: list() failed', self)
            raise RuntimeError('retrieve_message_ids() failed') from err
        else:
            _LOG.info('%s%s%s: pass_(%s) status: %s',
                      colorama.Style.DIM, self, colorama.Style.RESET_ALL, '***', status)

        if not status.startswith(b'+OK'):
            raise RuntimeError(f'pass_() status: "{status!r}"')

    def _connect_secure(self) -> bool:

        status = b''
        try:
            status = self._link.apop(self.login, self.password)
        except poplib.error_proto:
            _LOG.warning('%s: apop() failed', self)
        else:
            _LOG.info('%s%s%s: apop(%s, %s) status: %s',
                      colorama.Style.DIM, self, colorama.Style.RESET_ALL, self.login, '***', status)

        return status.startswith(b'+OK')

    # def stat(self) -> None:
    #     message_count, messages_size = self._link.stat()
    #     _LOG.debug('messages_count: %s', message_count)
    #     _LOG.debug('messages_size: %s', messages_size)

    def is_alive(self) -> bool:

        status = b''
        try:
            status = self._link.noop()
        except poplib.error_proto:
            _LOG.exception('%s: noop() failed', self)
        else:
            _LOG.info('%s%s%s: noop() status: %s',
                      colorama.Style.DIM, self, colorama.Style.RESET_ALL, status)

        return status.startswith(b'+OK')

    def retrieve_message_ids(self) -> t.List[int]:
        """Retrieve list of message IDs."""
        status = b''
        try:
            status, message_ids, octets = self._link.list()
        except poplib.error_proto as err:
            _LOG.exception('%s: list() failed', self)
            raise RuntimeError('retrieve_message_ids() failed') from err
        else:
            _LOG.info(
                '%s%s%s: list() status: %s, message_ids: %s%s%s, octets: %s%s%s',
                colorama.Style.DIM, self, colorama.Style.RESET_ALL, status,
                colorama.Style.DIM, [r.decode() for r in message_ids], colorama.Style.RESET_ALL,
                colorama.Style.DIM, octets, colorama.Style.RESET_ALL)

        if not status.startswith(b'+OK'):
            raise RuntimeError('retrieve_message_ids() failed')

        return [int(message_id.decode().split()[0]) for message_id in message_ids]

    def retrieve_message_lines(self, message_id: int) -> t.List[bytes]:
        """Retrieve raw contents of a message with a given ID as list of byte lines."""
        status = b''
        try:
            status, message_lines, octets = self._link.retr(message_id)
        except poplib.error_proto as err:
            _LOG.exception('%s: retr(%i) failed', self, message_id)
            raise RuntimeError('retrieve_message_lines() failed') from err
        else:
            _LOG.info(
                '%s%s%s: retr(%i) status: %s, len(message_lines): %s, octets: %s',
                colorama.Style.DIM, self, colorama.Style.RESET_ALL,
                message_id, status, len(message_lines), octets)

        if not status.startswith(b'+OK'):
            raise RuntimeError('retrieve_message_lines() failed')

        return message_lines

    def disconnect(self) -> None:

        status = b''
        try:
            status = self._link.quit()
        except poplib.error_proto as err:
            _LOG.exception('%s: quit() failed', self)
            raise RuntimeError('disconnect() failed') from err
        else:
            _LOG.info('%s%s%s: quit() status: %s',
                      colorama.Style.DIM, self, colorama.Style.RESET_ALL, status)

        if not status.startswith(b'+OK'):
            raise RuntimeError('disconnect() failed')
