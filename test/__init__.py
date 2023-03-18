"""Initialization of tests of maildaemon package."""

import logging

from maildaemon._logging import configure_logging

configure_logging()
logging.getLogger().setLevel(logging.DEBUG)
