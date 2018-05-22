
import typing as t
import unittest

from maildaemon.config import load_config
from maildaemon.imap_daemon import IMAPDaemon
from maildaemon.message_filter import MessageFilter


class Tests(unittest.TestCase):

    config = load_config()

    def test_construct(self):
        def func1(arg: str):
            return True
        def func2(arg: t.Any):
            return
        conn = None  # type: Connection
        connections = [conn]
        msg_filter = MessageFilter(connections, [[('aa', func1)]], [func2])
        self.assertIsNotNone(msg_filter)

    @unittest.skip('temporary')
    def test_apply(self):

        c = IMAPDaemon.from_dict(self.config['connections']['gmail-imap'])

        c.connect()

        msg = c.retrieve_message(1)

        f = MessageFilter.from_dict(self.config['filters']['facebook'], {'gmail-imap': c})
        result = f.applies_to(msg)
        self.assertIsInstance(result, bool, msg=(f, msg))

        c.disconnect()
