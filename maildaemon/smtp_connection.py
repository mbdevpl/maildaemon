
import logging
import smtplib
import typing as t

from .connection import Connection

_LOG = logging.getLogger(__name__)

TIMEOUT = 10

class SMTPConnection(Connection):
    """
    For handling SMTP connections.
    """

    ports = [25, 465, 587]
    ssl_ports = [465, 587]

    def __init__(self, domain: str, ssl: bool=True, port: t.Optional[int]=None):
        super().__init__(domain, ssl, port)

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

    def send_message(self, message) -> None:

        #status = self._link.send_message(msg, to_addrs=message.to_address)
        #_LOG.debug('send_message() status: %s', status)
        pass

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
