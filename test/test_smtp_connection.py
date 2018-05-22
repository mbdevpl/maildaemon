
import email
import os
import unittest

from maildaemon.config import load_config
from maildaemon.imap_connection import IMAPConnection
from maildaemon.smtp_connection import SMTPConnection


@unittest.skipUnless(os.environ.get('TEST_COMM') or os.environ.get('CI'),
                     'skipping tests that require server connection')
class Tests(unittest.TestCase):

    config = load_config()

    @unittest.skip('temporary')
    def test_connect(self):

        s = SMTPConnection.from_dict(self.config['connections']['test-smtp'])
        s.connect()
        s.disconnect()

    @unittest.skip('temporary')
    def test_send_message(self):

        c = IMAPConnection.from_dict(self.config['connections']['test-imap'])
        c.connect()
        _, body = c.retrieve_message_parts(1, ['BODY.PEEK[]'])
        c.disconnect()

        message = email.message_from_bytes(body)

        # print(message.as_string())
        # print(message.keys())

        s = SMTPConnection.from_dict(self.config['connections']['test-smtp'])
        s.connect()

        del message['Subject']
        message['Subject'] = 'test'
        del message['From']
        message['From'] = s.login
        del message['To']
        message['To'] = s.login
        # message['Envelope-To'] = s.login
        s.send_message(message)

        s.disconnect()
