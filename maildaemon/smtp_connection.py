"""For handling SMTP connections."""

import email.message
import logging
import smtplib
import typing as t

from .connection import Connection

_LOG = logging.getLogger(__name__)

TIMEOUT = 10


class SMTPConnection(Connection):
    """For handling SMTP connections."""

    ports = [25, 465, 587]
    ssl_ports = [465, 587]

    def __init__(self, domain: str, port: t.Optional[int] = None, ssl: bool = True):
        super().__init__(domain, port, ssl)

        self._link: t.Union[smtplib.SMTP, smtplib.SMTP_SSL]
        if self.ssl:
            self._link = smtplib.SMTP_SSL(self.domain, self.port, timeout=TIMEOUT)
        else:
            self._link = smtplib.SMTP(self.domain, self.port, timeout=TIMEOUT)

        if not self.ssl:
            self._upgrade_connection()

    def _upgrade_connection(self) -> None:
        if self.ssl:
            return

        status = 0
        try:
            status, response = self._link.starttls()
        except smtplib.SMTPException:
            _LOG.warning('%s: starttls() failed', self)
        else:
            _LOG.info('%s: starttls() status: %s, response: %s', self, status, response.decode())

        if status in range(200, 300):
            self.ssl = True
            _LOG.info('%s: connection upgraded to TLS', self)

    def connect(self) -> None:
        status = 0
        try:
            status, response = self._link.login(self.login, self.password)
        except smtplib.SMTPException as err:
            _LOG.exception('%s: login(%s, %s) failed', self, self.login, '***')
            raise RuntimeError('connect() failed') from err
        else:
            _LOG.info(
                '%s: login(%s, %s) status: %s, response: %s',
                self, self.login, '***', status, response.decode())

        if status not in range(200, 300):
            raise RuntimeError('connect() failed')

    def is_alive(self) -> bool:
        status = 0
        try:
            status, response = self._link.noop()
        except smtplib.SMTPException:
            _LOG.exception('%s: noop() failed', self)
        else:
            _LOG.info('%s: noop() status: %s, response: %s', self, status, response.decode())

        return status in range(200, 300)

    def send_message(self, message: email.message.Message) -> None:
        """Send an e-mail using SMTP."""
        status = None
        try:
            status = self._link.send_message(message)
        except smtplib.SMTPException as err:
            _LOG.exception('%s: send_message(%s) failed', self, '***')
            raise RuntimeError('send_message() failed') from err
        else:
            _LOG.info('%s: send_message(%s) status: %s', self, '***', status)

        if not isinstance(status, dict) or len(status) > 0:
            raise RuntimeError('send_message() failed')

    def disconnect(self) -> None:
        status = 0
        try:
            status, response = self._link.quit()
        except smtplib.SMTPException as err:
            _LOG.exception('%s: quit() failed', self)
            raise RuntimeError('disconnect() failed') from err
        else:
            _LOG.info('%s: quit() status: %s, response: %s', self, status, response.decode())

        if status not in range(200, 300):
            raise RuntimeError('disconnect() failed')
