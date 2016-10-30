
import logging
import time
import unittest

from maildaemon.config import load_config
from maildaemon.imap_connection import IMAPConnection

_LOG = logging.getLogger(__name__)

class Test(unittest.TestCase):

    config = load_config()

    def test_retrieve_messages_parts(self):

        for connection_name in ['test-imap', 'test-imap-ssl']:
            with self.subTest(msg=connection_name):
                c = IMAPConnection.from_dict(self.config['connections'][connection_name])

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
        #c.disconnect()
