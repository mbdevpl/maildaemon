
import unittest

from maildaemon.config import load_config
from maildaemon.imap_connection import IMAPConnection

class TestIMAPConnection(unittest.TestCase):

    config = load_config()

    def test_retrieve_messages_parts(self):

        c = IMAPConnection.from_dict(self.config['connections']['gmail-imap'])

        c.connect()
        c.open_folder()
        _ = c.retrieve_messages_parts([1, 2], ['UID', 'ENVELOPE'])
        for env, msg in _:
            #print('uid+envelope', len(env), len(msg) if isinstance(msg, bytes) else msg)
            self.assertGreater(len(env), 0, msg=_)
            self.assertIsNone(msg, msg=_)
        _ = c.retrieve_messages_parts([1, 2], ['BODY.PEEK[]'])
        for env, msg in _:
            #print('body', len(env), len(msg) if isinstance(msg, bytes) else msg)
            self.assertGreater(len(env), 0, msg=_)
            self.assertGreater(len(msg), 0, msg=_)
        c.close_folder()
        alive = c.is_alive()
        self.assertTrue(alive, msg=c)
        c.disconnect()
