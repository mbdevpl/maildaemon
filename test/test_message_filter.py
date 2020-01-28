"""Test filtering of messages."""

import logging
import os
import pathlib
import typing as t
import unittest

from maildaemon.config import load_config
from maildaemon.connection import Connection
from maildaemon.imap_connection import IMAPConnection
from maildaemon.imap_cache import IMAPCache
from maildaemon.message_filter import MessageFilter

_LOG = logging.getLogger(__name__)

_HERE = pathlib.Path(__file__).parent
_TEST_CONFIG_PATH = _HERE.joinpath('maildaemon_test_config.json')


class Tests(unittest.TestCase):

    config = load_config(_TEST_CONFIG_PATH)

    def test_construct(self):
        def func1(_: str):
            return True

        def func2(_: t.Any):
            return
        conn = None  # type: Connection
        connections = [conn]
        msg_filter = MessageFilter(connections, [[('aa', func1)]], [func2])
        self.assertIsNotNone(msg_filter)

    @unittest.skipUnless(os.environ.get('TEST_COMM') or os.environ.get('CI'),
                         'skipping test that requires server connection')
    def test_from_config(self):
        connection = IMAPConnection.from_dict(self.config['connections']['test-imap'])
        filter_ = MessageFilter.from_dict(self.config['filters']['facebook-notification'],
                                          {'test-imap': connection})
        self.assertIsNotNone(filter_)

    @unittest.skipUnless(os.environ.get('TEST_COMM') or os.environ.get('CI'),
                         'skipping test that requires server connection')
    def test_if_applies(self):
        connection = IMAPCache.from_dict(self.config['connections']['test-imap'])
        connection.connect()
        ids = connection.retrieve_message_ids()
        msg = connection.retrieve_message(ids[0])
        connection.disconnect()
        _LOG.debug('%s', msg.from_address)
        _LOG.debug('%s', msg.subject)

        filter_ = MessageFilter.from_dict(self.config['filters']['facebook-notification'],
                                          {'test-imap': connection})
        result = filter_.applies_to(msg)
        _LOG.debug('Does filter apply? %s', result)
        self.assertIsInstance(result, bool, msg=(filter_, msg))
        self.assertFalse(result)

        filter_ = MessageFilter.from_dict(self.config['filters']['test-message'],
                                          {'test-imap': connection})
        result = filter_.applies_to(msg)
        _LOG.debug('Does filter apply? %s', result)
        self.assertIsInstance(result, bool, msg=(filter_, msg))
        self.assertTrue(result)
