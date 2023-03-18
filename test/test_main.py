
import contextlib
import os
import pathlib
import unittest
import unittest.mock

from maildaemon.__main__ import main
from .test_setup import run_module

from .config import TEST_CONFIG_PATH


class Tests(unittest.TestCase):

    @unittest.skipUnless(os.environ.get('TEST_COMM') or os.environ.get('CI'),
                         'test requires server connection')
    def test_no_args(self):
        import maildaemon.config
        with unittest.mock.patch.object(maildaemon.config, 'DEFAULT_CONFIG_PATH',
                                        new=TEST_CONFIG_PATH):
            run_module('maildaemon')

    @unittest.skipUnless(os.environ.get('TEST_COMM') or os.environ.get('CI'),
                         'test requires server connection')
    def test_verbosity(self):
        import maildaemon.config
        with unittest.mock.patch.object(maildaemon.config, 'DEFAULT_CONFIG_PATH',
                                        new=TEST_CONFIG_PATH):
            run_module('maildaemon', '--verbose')
            run_module('maildaemon', '--quiet')
            run_module('maildaemon', '--debug')

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
