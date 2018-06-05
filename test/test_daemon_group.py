
import os
import pathlib
import unittest

from maildaemon.config import load_config
from maildaemon.connection_group import ConnectionGroup
from maildaemon.daemon_group import DaemonGroup

_HERE = pathlib.Path(__file__).parent
_TEST_CONFIG_PATH = _HERE.joinpath('maildaemon_test_config.json')


@unittest.skipUnless(os.environ.get('TEST_COMM') or os.environ.get('CI'),
                     'skipping tests that require server connection')
class Tests(unittest.TestCase):

    config = load_config(_TEST_CONFIG_PATH)

    def test_connection(self):
        conns = {'test-imap': self.config['connections']['test-imap'],
                 'test-imap-ssl': self.config['connections']['test-imap-ssl'],
                 'test-pop': self.config['connections']['test-pop'],
                 'test-pop-ssl': self.config['connections']['test-pop-ssl']}
        connections = ConnectionGroup.from_dict(conns)
        daemons = DaemonGroup(connections, [])
        self.assertEqual(len(daemons), 4)

    def test_run(self):
        conns = {'test-imap': self.config['connections']['test-imap'],
                 'test-imap-ssl': self.config['connections']['test-imap-ssl'],
                 'test-pop': self.config['connections']['test-pop'],
                 'test-pop-ssl': self.config['connections']['test-pop-ssl']}
        connections = ConnectionGroup.from_dict(conns)
        daemons = DaemonGroup(connections, [])
        self.assertEqual(len(daemons), 4)
        # daemons.run()  # TODO: there's some cryptic error in msg id 12 in INBOX
