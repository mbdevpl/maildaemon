"""Tests for handling e-mail messages."""

import email
import logging
import os
import pathlib
import unittest

from maildaemon.config import load_config
from maildaemon.imap_connection import IMAPConnection
from maildaemon.message import Message

_LOG = logging.getLogger(__name__)

_HERE = pathlib.Path(__file__).parent
_TEST_CONFIG_PATH = _HERE.joinpath('maildaemon_test_config.json')


class Tests(unittest.TestCase):

    def test_construct(self):
        message = Message()
        self.assertIsNotNone(message)

    @unittest.skipUnless(os.environ.get('TEST_COMM') or os.environ.get('CI'),
                         'skipping tests that require server connection')
    def test_from_email_message(self):
        config = load_config(_TEST_CONFIG_PATH)
        folder = 'INBOX'
        connection = IMAPConnection.from_dict(config['connections']['test-imap-ssl'])
        connection.connect()
        connection.open_folder(folder)
        ids = connection.retrieve_message_ids()
        messages_data = connection.retrieve_messages_parts(ids[:1], ['BODY.PEEK[]'])
        connection.disconnect()
        _, body = messages_data[0]
        message = Message(email.message_from_bytes(body), connection, folder, 1)
        _LOG.debug('%s', message.from_address)
        _LOG.debug('%s', message.subject)
        self.assertGreater(len(message.from_address), 0)
        self.assertGreater(len(str(message.subject)), 0)
