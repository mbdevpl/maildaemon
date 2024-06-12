"""Entry point of maildaemon package."""

import argparse
import logging
import pathlib

import boilerplates.logging
import colorama
import daemon

from ._version import VERSION as version
from .config import DEFAULT_CONFIG_PATH, load_config
from .connection_group import ConnectionGroup
from .message_filter import MessageFilter
from .daemon_group import DaemonGroup

_LOG = logging.getLogger(__name__)


class Logging(boilerplates.logging.Logging):
    """Logging configuration."""

    packages = ['maildaemon']
    # level_global = logging.INFO


class Formatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass


def parse_args(args=None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog='maildaemon',
        description=f'''Multi-server mail filtering daemon supporting IMAP, POP and SMTP.

Configuration is stored in "{DEFAULT_CONFIG_PATH}".

''', epilog='''examples:
  maildaemon -h
  maildaemon -d

Copyright 2016-2023  Mateusz Bysiek  https://mbdevpl.github.io/
''',
        formatter_class=Formatter, allow_abbrev=True)
    parser.version = version

    parser.add_argument(
        '--config', metavar='PATH', type=pathlib.Path, default=DEFAULT_CONFIG_PATH,
        help='''path to the configuration file;
        can be absolute, or relative to current woking directory''')
    parser.add_argument(
        '--daemon', '-d', action='store_true', default=False, required=False,
        help='''run as daemon''')

    parser.add_argument(
        '--quiet', '-q', action='store_true', default=False, required=False,
        help='''do not output anything but critical errors; overrides "--verbose" and "--debug"
        if present; sets logging level to CRITICAL''')

    parser.add_argument(
        '--verbose', '-v', action='store_true', default=False, required=False,
        help='''output non-critical information; sets logging level to INFO''')

    parser.add_argument(
        '--debug', action='store_true', default=False, required=False,
        help='''output information at debugging level; overrides "--verbose" if present; sets
        logging level to DEBUG''')

    parser.add_argument('--version', action='version')

    return parser.parse_args(args)


def main(args=None):
    """Command-line interface of maildaemon."""
    colorama.init()

    parsed_args = parse_args(args)

    if parsed_args.verbose:
        logging.getLogger().setLevel(logging.INFO)
    if parsed_args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    if parsed_args.quiet:
        logging.getLogger().setLevel(logging.CRITICAL)

    config = load_config(parsed_args.config)

    group = ConnectionGroup.from_dict(config['connections'])

    filters = []
    for _, filter_data in config['filters'].items():
        flt = MessageFilter.from_dict(filter_data, group.connections)
        filters.append(flt)

    daemon_group = DaemonGroup(group, filters)

    if parsed_args.daemon:
        with daemon.DaemonContext():
            daemon_group.run()
    else:
        daemon_group.run()


if __name__ == '__main__':
    Logging.configure()
    main()
