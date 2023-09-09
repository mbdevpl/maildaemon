"""Initialization of tests of maildaemon package."""

import logging

from maildaemon.__main__ import Logging


class TestsLogging(Logging):
    """Logging configuration."""

    level_global = logging.DEBUG


TestsLogging.configure()
