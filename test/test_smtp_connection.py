"""Tests for handling SMTP connections."""

import email
import os
import pathlib
import unittest

from maildaemon.config import load_config
from maildaemon.imap_connection import IMAPConnection
from maildaemon.smtp_connection import SMTPConnection

_HERE = pathlib.Path(__file__).parent
_TEST_CONFIG_PATH = _HERE.joinpath('maildaemon_test_config.json')


@unittest.skipUnless(os.environ.get('TEST_COMM') or os.environ.get('CI'),
                     'skipping tests that require server connection')
class Tests(unittest.TestCase):

    config = load_config(_TEST_CONFIG_PATH)

    @unittest.skipUnless(os.environ.get('TEST_SMTP'), 'skipping SMTP-related test')
    def test_connect(self):
        smtp = SMTPConnection.from_dict(self.config['connections']['test-smtp'])
        smtp.connect()
        smtp.disconnect()

    @unittest.skipUnless(os.environ.get('TEST_SMTP'), 'skipping SMTP-related test')
    def test_send_message(self):
        imap = IMAPConnection.from_dict(self.config['connections']['test-imap'])
        imap.connect()
        _, body = imap.retrieve_message_parts(1, ['BODY.PEEK[]'])
        imap.disconnect()

        message = email.message_from_bytes(body)

        smtp = SMTPConnection.from_dict(self.config['connections']['test-smtp'])
        smtp.connect()
        del message['Subject']
        message['Subject'] = 'test'
        del message['From']
        message['From'] = 'dummy@domain.com'
        del message['To']
        message['To'] = 'dummy@domain.com'
        smtp.send_message(message)
        smtp.disconnect()
