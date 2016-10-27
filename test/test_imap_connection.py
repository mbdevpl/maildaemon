
import unittest

from maildaemon.config import load_config
from maildaemon.imap_connection import IMAPConnection

class TestIMAPConnection(unittest.TestCase):

    config = load_config()

    def test_retrieve_messages_parts(self):

        c = IMAPConnection.from_dict(self.config['connections']['gmail-imap'])

        c.connect()
        c.open_folder()
        _ = c.retrieve_messages_parts([1, 2], ['ENVELOPE'])
        for env, msg in _:
            print(1, len(env), len(msg) if isinstance(msg, bytes) else msg)
        _ = c.retrieve_messages_parts([1, 2], ['UID', 'ENVELOPE'])
        for env, msg in _:
            print(2, len(env), len(msg) if isinstance(msg, bytes) else msg)
        _ = c.retrieve_messages_parts([1, 2], ['BODY.PEEK[]'])
        for env, msg in _:
            print(3, len(env), len(msg) if isinstance(msg, bytes) else msg)
        c.close_folder()
        c.disconnect()
