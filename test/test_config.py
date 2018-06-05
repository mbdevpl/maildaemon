"""Test configuration loader."""

import os
import pathlib
import unittest

from maildaemon.config import load_config

_HERE = pathlib.Path(__file__).parent
_TEST_CONFIG_PATH = _HERE.joinpath('maildaemon_test_config.json')


class Tests(unittest.TestCase):

    def test_load_basic(self):
        cfg = load_config(_TEST_CONFIG_PATH)
        self.assertIn('connections', cfg, msg=cfg)
        self.assertGreater(len(cfg['connections']), 0, msg=cfg)

    def test_load_concrete_connections(self):
        cfg = load_config(_TEST_CONFIG_PATH)
        self.assertIn('connections', cfg, msg=cfg)
        self.assertGreater(len(cfg['connections']), 0, msg=cfg)
        self.assertIn('test-imap', cfg['connections'], msg=cfg)
        self.assertIn('test-pop', cfg['connections'], msg=cfg)

    def test_completeness(self):
        cfg = load_config(_TEST_CONFIG_PATH)
        self.assertIn('test-imap', cfg['connections'], msg=cfg)
        section = cfg['connections']['test-imap']
        self.assertIn('domain', section, msg=cfg)
        self.assertIn('ssl', section, msg=cfg)
        self.assertIn('port', section, msg=cfg)
        self.assertIn('login', section, msg=cfg)
        self.assertIn('password', section, msg=cfg)

    def test_missing_protocol(self):
        config_filename = '.maildaemon.config.tmp'
        with open(config_filename, 'w') as cfg_file:
            print(r'''{"connections": {"missing-protocol": {"domain": "example.com"}}}''',
                  file=cfg_file)
        with self.assertRaises(ValueError):
            load_config(config_filename)
        os.remove(config_filename)

    def test_missing_domain(self):
        config_filename = '.maildaemon.config.tmp'
        with open(config_filename, 'w') as cfg_file:
            print(r'''{"connections": {"missing-protocol": {"protocol": "IMAP"}}}''', file=cfg_file)
        with self.assertRaises(ValueError):
            load_config(config_filename)
        os.remove(config_filename)

    def test_missing_filter_action(self):
        config_filename = '.maildaemon.config.tmp'
        with open(config_filename, 'w') as cfg_file:
            print(r'''{"filters": {"empty": {}}}''', file=cfg_file)
        with self.assertRaises(ValueError):
            load_config(config_filename)
        os.remove(config_filename)
