
import logging
import os
import unittest

from maildaemon.config import load_config
from maildaemon.imap_daemon import IMAPDaemon

_LOG = logging.getLogger(__name__)


@unittest.skipUnless(os.environ.get('TEST_COMM') or os.environ.get('CI'),
                     'skipping tests that require server connection')
class Tests(unittest.TestCase):

    config = load_config()

    @unittest.skip('...')
    def test_update_folders(self):
        for connection_name in ['test-imap', 'test-imap-ssl']:
            with self.subTest(msg=connection_name):
                c = IMAPDaemon.from_dict(self.config['connections'][connection_name])
                c.connect()
                c.update_folders()
                folder = c.folders[-1]
                # c.delete_folder(folder)  # TODO: implement IMAP folder deletion
                c.update_folders()
                c.disconnect()

    def test_update(self):
        for connection_name in ['test-imap', 'test-imap-ssl']:
            with self.subTest(msg=connection_name):
                # import time; time.sleep(2)
                c = IMAPDaemon.from_dict(self.config['connections'][connection_name])
                c.connect()
                # c.update()  # TODO: there's some cryptic error in msg id 12
                c.disconnect()
