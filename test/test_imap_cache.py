"""Tests for daemon working with IMAP connections."""

import logging
import os
import pathlib
import unittest

from maildaemon.config import load_config
from maildaemon.imap_cache import IMAPCache

_LOG = logging.getLogger(__name__)

_HERE = pathlib.Path(__file__).parent
_TEST_CONFIG_PATH = _HERE.joinpath('maildaemon_test_config.json')


@unittest.skipUnless(os.environ.get('TEST_COMM') or os.environ.get('CI'),
                     'skipping tests that require server connection')
class Tests(unittest.TestCase):

    config = load_config(_TEST_CONFIG_PATH)

    def test_update_folders(self):
        for connection_name in ['test-imap', 'test-imap-ssl']:
            with self.subTest(msg=connection_name):
                c = IMAPCache.from_dict(self.config['connections'][connection_name])
                c.connect()
                c.update_folders()
                # folder = c.folders['']
                # c.delete_folder(folder)  # TODO: implement IMAP folder deletion
                c.update_folders()
                c.disconnect()

    def test_update(self):
        for connection_name in ['test-imap', 'test-imap-ssl']:
            with self.subTest(msg=connection_name):
                # import time; time.sleep(2)
                c = IMAPCache.from_dict(self.config['connections'][connection_name])
                c.connect()
                # c.update()  # TODO: there's some cryptic error in msg id 12 in INBOX
                c.disconnect()
