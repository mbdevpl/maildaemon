
import ast
import os
import unittest

from maildaemon.config import load_config

class Test(unittest.TestCase):

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

        self.assertIn('test-imap', cfg['connections'], msg=cfg)
        #self.assertIn('gmail-smtp', cfg['connections'], msg=cfg)

    def test_load_config_completeness(self):

        cfg = load_config()

        self.assertIn('test-imap', cfg['connections'], msg=cfg)

        section = cfg['connections']['test-imap']
        self.assertIn('domain', section, msg=cfg)
        self.assertIn('ssl', section, msg=cfg)
        self.assertIn('port', section, msg=cfg)
        self.assertIn('login', section, msg=cfg)
        self.assertIn('password', section, msg=cfg)

    def test_config_missing_protocol(self):

        config_filename = '.maildaemon.config.tmp'

        with open(config_filename, 'w') as f:
            print('''[connection: missing-protocol]\n  domain = example.com''', file=f)

        with self.assertRaises(RuntimeError):
            cfg = load_config(config_filename)
            self.assertIsNone(cfg, msg=cfg)

        os.remove(config_filename)

    def test_config_missing_domain(self):

        config_filename = '.maildaemon.config.tmp'

        with open(config_filename, 'w') as f:
            print('''[connection: missing-domain]\n  protocol = IMAP''', file=f)

        with self.assertRaises(RuntimeError):
            cfg = load_config(config_filename)
            self.assertIsNone(cfg, msg=cfg)

        os.remove(config_filename)

    def test_config_missing_filter_action(self):

        config_filename = '.maildaemon.config.tmp'

        with open(config_filename, 'w') as f:
            print('''[filter: empty]''', file=f)

        with self.assertRaises(RuntimeError):
            cfg = load_config(config_filename)
            self.assertIsNone(cfg, msg=cfg)

        os.remove(config_filename)
