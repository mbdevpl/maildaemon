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
            _LOG.info('%s: starttls() status: %s, response: %s', self, status, response.decode())
        except smtplib.SMTPException:
            _LOG.warning('%s: starttls() failed', self)

        if status in range(200, 300):
            self.ssl = True
            _LOG.info('%s: connection upgraded to TLS', self)

    def connect(self) -> None:
        status = 0
        try:
            status, response = self._link.login(self.login, self.password)
            _LOG.info(
                '%s: login(%s, %s) status: %s, response: %s',
                self, self.login, '***', status, response.decode())
        except smtplib.SMTPException as err:
            _LOG.exception('%s: login(%s, %s) failed', self, self.login, '***')
            raise RuntimeError('connect() failed') from err

        if status not in range(200, 300):
            raise RuntimeError('connect() failed')

    def is_alive(self) -> bool:
        status = 0
        try:
            status, response = self._link.noop()
            _LOG.info('%s: noop() status: %s, response: %s', self, status, response.decode())
        except smtplib.SMTPException:
            _LOG.exception('%s: noop() failed', self)

        return status in range(200, 300)

    def send_message(self, message: email.message.Message) -> None:
        status = None
        try:
            status = self._link.send_message(message)
            _LOG.info('%s: send_message(%s) status: %s', self, '***', status)
        except smtplib.SMTPException as err:
            _LOG.exception('%s: send_message(%s) failed', self, '***')
            raise RuntimeError('send_message() failed') from err

        if not isinstance(status, dict) or len(status) > 0:
            raise RuntimeError('send_message() failed')

    def disconnect(self) -> None:
        status = 0
        try:
            status, response = self._link.quit()
            _LOG.info('%s: quit() status: %s, response: %s', self, status, response.decode())
        except smtplib.SMTPException as err:
            _LOG.exception('%s: quit() failed', self)
            raise RuntimeError('disconnect() failed') from err

        if status not in range(200, 300):
            raise RuntimeError('disconnect() failed')
