
import ast
import unittest

from maildaemon.config import load_config

class TestConfig(unittest.TestCase):

    def test_methodology(self):

        #self.assertTrue(bool('True')) # correct by accident
        #self.assertFalse(bool('False')) # wrong
        self.assertTrue(ast.literal_eval('True'))
        self.assertFalse(ast.literal_eval('False'))

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

    def test_load_config_completeness(self):

        cfg = load_config()

        self.assertIn('gmail-imap', cfg['connections'], msg=cfg)

        section = cfg['connections']['gmail-imap']
        self.assertIn('domain', section, msg=cfg)
        self.assertIn('ssl', section, msg=cfg)
        self.assertIn('port', section, msg=cfg)
        self.assertIn('login', section, msg=cfg)
        self.assertIn('password', section, msg=cfg)
