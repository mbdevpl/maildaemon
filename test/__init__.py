"""This is "__init__.py" file of tests for maildaemon."""

import logging

from maildaemon._logging import configure_logging

configure_logging()
logging.getLogger().setLevel(logging.DEBUG)
