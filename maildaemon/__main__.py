"""Entry point of maildaemon package."""

# import logging

import boilerplates.logging

from .cli import main


class Logging(boilerplates.logging.Logging):
    """Logging configuration."""

    packages = ['maildaemon']
    # level_global = logging.WARNING


if __name__ == '__main__':
    Logging.configure()
    main()
