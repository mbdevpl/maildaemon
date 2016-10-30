
import unittest

from maildaemon.config import load_config
from maildaemon.pop_connection import POPConnection

class Test(unittest.TestCase):

    config = load_config()

    def test_retrieve_message_ids(self):

        for connection_name in ['test-pop', 'test-pop-ssl']:
            with self.subTest(msg=connection_name):
                c = POPConnection.from_dict(self.config['connections'][connection_name])
                c.connect()
                ids = c.retrieve_message_ids()
                self.assertIsInstance(ids, list, msg=c)
                alive = c.is_alive()
                self.assertTrue(alive, msg=c)
                c.disconnect()
