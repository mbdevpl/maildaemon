
import logging

import oauth2
import oauth2.clients.imap

from .imap_daemon import IMAPDaemon

_LOG = logging.getLogger(__name__)


class GmailIMAPDaemon(IMAPDaemon):

    def connect_oauth(
            self, consumer_key: str, consumer_secret: str,
            user_token: str, user_secret: str) -> None:

        if not self.ssl:
            raise RuntimeError('only SSL-enabled connections are supported when using OAuth2')

        url = 'https://mail.google.com/mail/b/{}/imap/'.format(self.login)
        consumer = oauth2.Consumer(consumer_key, consumer_secret)
        token = oauth2.Token(user_token, user_secret)
        self._link = oauth2.clients.imap.IMAP4_SSL(self.domain, self.port)

        status, response = self._link.authenticate(url, consumer, token)
        _LOG.debug('authenticate() status: %s', status)
        _LOG.debug('response: %s', [r.decode() for r in response])
        if status != 'OK':
            raise RuntimeError('login() status: "{}"'.format(status))

    def update_folders(self):
        super().update_folders()
        del self.folders['[Gmail]']
        _LOG.info('%s: unusable folder "%s" was deleted', self, '[Gmail]')

    # TODO: handling of duplicate messages that occur because of Gmail tags
