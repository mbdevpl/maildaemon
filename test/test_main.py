
import contextlib
import os
import unittest

from maildaemon.__main__ import main
from .test_setup import run_module


class Tests(unittest.TestCase):

    def test_bad_run(self):
        with self.assertRaises(SystemExit):
            run_module('maildaemon', '--not-a-valid-option')
        run_module('maildaemon', run_name='not_main')

    def test_help(self):
        with open(os.devnull, 'a') as devnull:
            for flags in (['-h'], ['--help']):
                with self.assertRaises(SystemExit):
                    with contextlib.redirect_stdout(devnull):
                        main(flags)
