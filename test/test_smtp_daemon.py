"""Tests for daemon working with SMTP connections."""

import email
import logging
import os
import pathlib
import unittest

from maildaemon.config import load_config
from maildaemon.imap_connection import IMAPConnection
from maildaemon.smtp_daemon import SMTPDaemon

_LOG = logging.getLogger(__name__)

_HERE = pathlib.Path(__file__).parent
_TEST_CONFIG_PATH = _HERE.joinpath('maildaemon_test_config.json')


@unittest.skipUnless(os.environ.get('TEST_COMM') or os.environ.get('CI'),
                     'skipping tests that require server connection')
class Tests(unittest.TestCase):

    config = load_config(_TEST_CONFIG_PATH)

    @unittest.skipUnless(os.environ.get('TEST_SMTP'), 'skipping SMTP-related test')
    def test_update(self):
        imap = IMAPConnection.from_dict(self.config['connections']['test-imap'])
        imap.connect()
        _, body = imap.retrieve_message_parts(1, ['BODY.PEEK[]'])
        imap.disconnect()

        message = email.message_from_bytes(body)

        connection = SMTPDaemon.from_dict(self.config['connections']['test-smtp'])
        connection.connect()
        connection.add_to_outbox(message)
        self.assertGreater(len(connection.outbox), 0, msg=connection)
        connection.update()
        connection.disconnect()
        self.assertEqual(len(connection.outbox), 0, msg=connection)
