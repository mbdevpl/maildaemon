
import os
import pathlib
import unittest

from maildaemon.config import load_config
from maildaemon.connection_group import ConnectionGroup

_HERE = pathlib.Path(__file__).parent
_TEST_CONFIG_PATH = _HERE.joinpath('maildaemon_test_config.json')


@unittest.skipUnless(os.environ.get('TEST_COMM') or os.environ.get('CI'),
                     'skipping tests that require server connection')
class Tests(unittest.TestCase):

    config = load_config(_TEST_CONFIG_PATH)

    def test_connection(self):
        conns = {'test-imap': self.config['connections']['test-imap'],
                 'test-imap-ssl': self.config['connections']['test-imap-ssl'],
                 'test-pop-ssl': self.config['connections']['test-pop-ssl']}
        connections = ConnectionGroup.from_dict(conns)
        self.assertEqual(len(connections), 3)
        connections.connect_all()
        connections.disconnect_all()

    def test_purge_dead(self):
        conns = {'test-imap-ssl': self.config['connections']['test-imap-ssl'],
                 'test-pop': self.config['connections']['test-pop'],
                 'test-pop-ssl': self.config['connections']['test-pop-ssl']}
        connections = ConnectionGroup.from_dict(conns)
        self.assertEqual(len(connections), 3)
        connections.connect_all()
        connections.purge_dead()
        connections.disconnect_all()
