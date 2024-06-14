"""Test the command-line interface."""

import contextlib
import os
import pathlib
import tempfile
import unittest
import unittest.mock

from boilerplates.packaging_tests import run_module

from maildaemon.cli import main

from .config import TEST_CONFIG_PATH


class Tests(unittest.TestCase):

    @unittest.skipUnless(os.environ.get('TEST_COMM') or os.environ.get('CI'),
                         'test requires server connection')
    def test_no_args(self):
        run_module('maildaemon', '--config', str(TEST_CONFIG_PATH), '-vv')

    @unittest.skipUnless(os.environ.get('TEST_COMM') or os.environ.get('CI'),
                         'test requires server connection')
    def test_verbosity(self):
        run_module('maildaemon', '--config', str(TEST_CONFIG_PATH), '--verbose')
        run_module('maildaemon', '--config', str(TEST_CONFIG_PATH), '--quiet')
        run_module('maildaemon', '--config', str(TEST_CONFIG_PATH), '-vv')

    def test_bad_run(self):
        with self.assertRaises(SystemExit):
            run_module('maildaemon', '--not-a-valid-option')
        run_module('maildaemon', run_name='not_main')

    def test_help(self):
        with open(os.devnull, 'w', encoding='utf-8') as devnull:
            for flags in (['-h'], ['--help']):
                with self.assertRaises(SystemExit):
                    with contextlib.redirect_stdout(devnull):
                        main(flags)

    def test_nonexisting_config(self):
        with tempfile.NamedTemporaryFile() as temp_file:
            created_file = pathlib.Path(temp_file.name)
        self.assertFalse(created_file.exists())
        with open(os.devnull, 'w', encoding='utf-8') as devnull:
            with self.assertRaises(FileNotFoundError):
                with contextlib.redirect_stdout(devnull):
                    main(['--config', str(created_file), '-vv'])

    @unittest.skipUnless(os.environ.get('TEST_COMM') or os.environ.get('CI'),
                         'test requires server connection')
    def test_daemon(self):
        main(['--config', str(TEST_CONFIG_PATH), '-vv', '-d'])
