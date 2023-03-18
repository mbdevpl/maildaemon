"""Tests for handling SMTP connections."""

import email
import os
import unittest

from maildaemon.config import load_config
from maildaemon.smtp_connection import SMTPConnection

from .config import TEST_CONFIG_PATH, TEST_MESSAGE_1_PATH, TEST_MESSAGE_2_PATH


@unittest.skipUnless(os.environ.get('TEST_COMM') or os.environ.get('CI'),
                     'skipping tests that require server connection')
class Tests(unittest.TestCase):

    config = load_config(TEST_CONFIG_PATH)

    def test_connect(self):
        smtp = SMTPConnection.from_dict(self.config['connections']['test-smtp'])
        smtp.connect()
        smtp.disconnect()

    def test_connect_ssl(self):
        smtp = SMTPConnection.from_dict(self.config['connections']['test-smtp-ssl'])
        smtp.connect()
        smtp.disconnect()

    def test_send_message(self):
        with TEST_MESSAGE_1_PATH.open(encoding='utf-8') as email_file:
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
        with TEST_MESSAGE_2_PATH.open(encoding='utf-8') as email_file:
            message = email.message_from_file(email_file)

        smtp = SMTPConnection.from_dict(self.config['connections']['test-smtp-ssl'])
        smtp.connect()
        for _ in range(5):
            smtp.send_message(message)
        message['To'] = 'pop-ssl@domain.com'
        for _ in range(5):
            smtp.send_message(message)
        smtp.disconnect()
