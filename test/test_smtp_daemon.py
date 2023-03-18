"""Tests for daemon working with SMTP connections."""

import email
import logging
import os
import unittest

from maildaemon.config import load_config
from maildaemon.smtp_daemon import SMTPDaemon

from .config import TEST_CONFIG_PATH, TEST_MESSAGE_1_PATH

_LOG = logging.getLogger(__name__)


@unittest.skipUnless(os.environ.get('TEST_COMM') or os.environ.get('CI'),
                     'skipping tests that require server connection')
class Tests(unittest.TestCase):

    config = load_config(TEST_CONFIG_PATH)

    def test_update(self):
        with TEST_MESSAGE_1_PATH.open(encoding='utf-8') as email_file:
            message = email.message_from_file(email_file)

        connection = SMTPDaemon.from_dict(self.config['connections']['test-smtp'])
        connection.connect()
        connection.add_to_outbox(message)
        self.assertGreater(len(connection.outbox), 0, msg=connection)
        connection.update()
        connection.disconnect()
        self.assertEqual(len(connection.outbox), 0, msg=connection)
