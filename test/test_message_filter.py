"""Test filtering of messages."""

import pathlib
import typing as t
import unittest

from maildaemon.config import load_config
from maildaemon.imap_connection import IMAPConnection
from maildaemon.imap_daemon import IMAPDaemon
from maildaemon.message_filter import MessageFilter

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

    def test_from_config(self):
        connection = IMAPConnection.from_dict(self.config['connections']['test-imap'])
        filter_ = MessageFilter.from_dict(self.config['filters']['facebook-notification'],
                                          {'test-imap': connection})
        self.assertIsNotNone(filter_)

    @unittest.skip('temporary')
    def test_apply(self):

        c = IMAPDaemon.from_dict(self.config['connections']['gmail-imap'])

        c.connect()

        msg = c.retrieve_message(1)

        f = MessageFilter.from_dict(self.config['filters']['facebook'], {'gmail-imap': c})
        result = f.applies_to(msg)
        self.assertIsInstance(result, bool, msg=(f, msg))

        c.disconnect()
