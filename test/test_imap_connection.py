"""Tests for IMAP connection handling."""

import logging
import os
import pathlib
import time
import unittest

from maildaemon.config import load_config
from maildaemon.imap_connection import IMAPConnection

_LOG = logging.getLogger(__name__)

_HERE = pathlib.Path(__file__).parent
_TEST_CONFIG_PATH = _HERE.joinpath('maildaemon_test_config.json')


@unittest.skipUnless(os.environ.get('TEST_COMM') or os.environ.get('CI'),
                     'skipping tests that require server connection')
class Tests(unittest.TestCase):

    config = load_config(_TEST_CONFIG_PATH)

    def test_retrieve_folders(self):
        for connection_name in ['test-imap', 'test-imap-ssl']:
            with self.subTest(msg=connection_name):
                connection = IMAPConnection.from_dict(self.config['connections'][connection_name])
                connection.connect()
                folders = connection.retrieve_folders()
                connection.disconnect()
                self.assertGreater(len(folders), 0, msg=connection)
                self.assertIn('INBOX', folders, msg=connection)

    def test_retrieve_message_ids(self):
        for connection_name in ['test-imap', 'test-imap-ssl']:
            with self.subTest(msg=connection_name):
                connection = IMAPConnection.from_dict(self.config['connections'][connection_name])
                connection.connect()
                connection.open_folder('INBOX')
                ids = connection.retrieve_message_ids('INBOX')
                connection.disconnect()
                self.assertIsInstance(ids, list, msg=type(ids))
                for id_ in ids:
                    self.assertIsInstance(id_, int, msg=ids)

    def test_retrieve_messages_parts(self):
        for connection_name in ['test-imap', 'test-imap-ssl']:
            with self.subTest(msg=connection_name):
                connection = IMAPConnection.from_dict(self.config['connections'][connection_name])
                connection.connect()
                connection.open_folder()
                ids = connection.retrieve_message_ids()
                msgs1 = connection.retrieve_messages_parts(ids[:2], ['UID', 'ENVELOPE'])
                msgs2 = connection.retrieve_messages_parts(ids[:2], ['BODY.PEEK[]'])
                connection.close_folder()
                alive = connection.is_alive()
                connection.disconnect()
                for env, msg in msgs1:
                    # print('uid+envelope', len(env), len(msg) if isinstance(msg, bytes) else msg)
                    self.assertGreater(len(env), 0, msg=msgs1)
                    self.assertIsNone(msg, msg=msgs1)
                for env, msg in msgs2:
                    # print('body', len(env), len(msg) if isinstance(msg, bytes) else msg)
                    self.assertGreater(len(env), 0, msg=msgs2)
                    self.assertGreater(len(msg), 0, msg=msgs2)
                self.assertTrue(alive, msg=connection)

    def test_delete_message(self):
        connection = IMAPConnection.from_dict(self.config['connections']['test-imap-ssl'])
        connection.connect()
        ids = connection.retrieve_message_ids()
        connection.delete_message(ids[-1], 'INBOX')
        connection.purge_deleted_messages()
        # with self.assertRaises(RuntimeError):
        #     connection.delete_message(ids[-1], 'INBOX')
        connection.delete_message(ids[-2], 'INBOX', purge_immediately=True)
        connection.disconnect()

    @unittest.skip('long')
    def test_timeout(self):

        c = IMAPConnection.from_dict(self.config['connections']['gmail-imap'])

        _LOG.debug('sleeping for 5m20s...')
        time.sleep(5 * 60 + 20)
        _LOG.debug('finished sleeping')

        c.connect()
        # works after 1m, 2m, 5m, 5m15s
        # doesn't work after 5m20s, 5m30s, 6m, 7m, 9m, 10m, 15m

    @unittest.skip('long')
    def test_timeout_after_connect(self):

        c = IMAPConnection.from_dict(self.config['connections']['gmail-imap'])
        c.connect()

        _LOG.debug('sleeping for 5 minutes...')
        time.sleep(5 * 60)
        _LOG.debug('finished sleeping')

        self.assertTrue(c.is_alive())

        _LOG.debug('sleeping for 5.5 minutes...')
        time.sleep(5.5 * 60)
        _LOG.debug('finished sleeping')

        self.assertFalse(c.is_alive())
        # c.disconnect()
