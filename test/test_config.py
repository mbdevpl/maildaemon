
import unittest

from maildaemon.config import load_config

class TestConfig(unittest.TestCase):

    def test_load_config_basic(self):

        cfg = load_config()
        self.assertIn('connections', cfg, msg=cfg)
        self.assertGreater(len(cfg['connections']), 0, msg=cfg)

    def test_load_config_concrete_connections(self):

        cfg = load_config()
        self.assertIn('connections', cfg, msg=cfg)
        self.assertGreater(len(cfg['connections']), 0, msg=cfg)

        self.assertIn('gmail-imap', cfg['connections'], msg=cfg)
        self.assertIn('gmail-smtp', cfg['connections'], msg=cfg)
