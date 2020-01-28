"""Tests for handling SMTP connections."""

import email
import os
import pathlib
import unittest

from maildaemon.config import load_config
from maildaemon.smtp_connection import SMTPConnection

_HERE = pathlib.Path(__file__).parent
_TEST_CONFIG_PATH = _HERE.joinpath('maildaemon_test_config.json')


@unittest.skipUnless(os.environ.get('TEST_COMM') or os.environ.get('CI'),
                     'skipping tests that require server connection')
class Tests(unittest.TestCase):

    config = load_config(_TEST_CONFIG_PATH)

    def test_connect(self):
        smtp = SMTPConnection.from_dict(self.config['connections']['test-smtp'])
        smtp.connect()
        smtp.disconnect()

    def test_connect_ssl(self):
        smtp = SMTPConnection.from_dict(self.config['connections']['test-smtp-ssl'])
        smtp.connect()
        smtp.disconnect()

    def test_send_message(self):
        with _HERE.joinpath('message1.txt').open() as email_file:
            message = email.message_from_file(email_file)

        smtp = SMTPConnection.from_dict(self.config['connections']['test-smtp'])
        smtp.connect()
        for _ in range(5):
            smtp.send_message(message)
        message['To'] = 'pop@domain.com'
        for _ in range(5):
            smtp.send_message(message)
        smtp.disconnect()

    def test_send_message_ssl(self):
        with _HERE.joinpath('message2.txt').open() as email_file:
            message = email.message_from_file(email_file)

        smtp = SMTPConnection.from_dict(self.config['connections']['test-smtp-ssl'])
        smtp.connect()
        for _ in range(5):
            smtp.send_message(message)
        message['To'] = 'pop-ssl@domain.com'
        for _ in range(5):
            smtp.send_message(message)
        smtp.disconnect()
