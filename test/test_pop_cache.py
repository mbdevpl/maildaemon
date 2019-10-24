"""Tests for daemon working with POP connections."""

import logging
import os
import pathlib
import unittest

from maildaemon.config import load_config
from maildaemon.pop_cache import POPCache

_LOG = logging.getLogger(__name__)

_HERE = pathlib.Path(__file__).parent
_TEST_CONFIG_PATH = _HERE.joinpath('maildaemon_test_config.json')


@unittest.skipUnless(os.environ.get('TEST_COMM') or os.environ.get('CI'),
                     'skipping tests that require server connection')
class Tests(unittest.TestCase):

    config = load_config(_TEST_CONFIG_PATH)

    def test_update(self):
        for connection_name in ['test-pop', 'test-pop-ssl']:
            with self.subTest(msg=connection_name):
                connection = POPCache.from_dict(self.config['connections'][connection_name])
                connection.connect()
                connection.update()
                connection.disconnect()
                self.assertIn('INBOX', connection.folders, msg=connection)
                self.assertGreater(len(connection.folders['INBOX'].messages), 0, msg=connection)
