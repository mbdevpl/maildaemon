"""Tests for POP connection handling."""

import os
import pathlib
import unittest

from maildaemon.config import load_config
from maildaemon.pop_connection import POPConnection

_HERE = pathlib.Path(__file__).parent
_TEST_CONFIG_PATH = _HERE.joinpath('maildaemon_test_config.json')


@unittest.skipUnless(os.environ.get('TEST_COMM') or os.environ.get('CI'),
                     'skipping tests that require server connection')
class Tests(unittest.TestCase):

    config = load_config(_TEST_CONFIG_PATH)

    def test_retrieve_message_ids(self):
        for connection_name in ['test-pop', 'test-pop-ssl']:
            with self.subTest(msg=connection_name):
                connection = POPConnection.from_dict(self.config['connections'][connection_name])
                connection.connect()
                ids = connection.retrieve_message_ids()
                alive = connection.is_alive()
                connection.disconnect()
                self.assertIsInstance(ids, list, msg=connection)
                self.assertTrue(alive, msg=connection)

    def test_retrieve_message_lines(self):
        for connection_name in ['test-pop', 'test-pop-ssl']:
            with self.subTest(msg=connection_name):
                connection = POPConnection.from_dict(self.config['connections'][connection_name])
                connection.connect()
                lines = connection.retrieve_message_lines(1)
                self.assertGreater(len(lines), 0, msg=connection)
