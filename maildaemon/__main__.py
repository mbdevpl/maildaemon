"""Entry point of maildaemon package."""

import argparse
import logging
import pathlib

from boilerplates.cli import \
    ArgumentDefaultsAndRawDescriptionHelpFormatter, make_copyright_notice, add_version_option, \
    add_verbosity_group, get_logging_level
import boilerplates.logging
import colorama
import daemon

from ._version import VERSION
from .config import DEFAULT_CONFIG_PATH, load_config
from .connection_group import ConnectionGroup
from .message_filter import MessageFilter
from .daemon_group import DaemonGroup

_LOG = logging.getLogger(__name__)


class Logging(boilerplates.logging.Logging):
    """Logging configuration."""

    packages = ['maildaemon']
    # level_global = logging.INFO


def parse_args(args=None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog='maildaemon',
        description=f'''Multi-server mail filtering daemon supporting IMAP, POP and SMTP.

Configuration is stored in "{DEFAULT_CONFIG_PATH}".''',
        epilog=f'''examples:
  maildaemon -h
  maildaemon -d

{make_copyright_notice(2016, 2024, url='https://github.com/mbdevpl/maildaemon')}''',
        formatter_class=ArgumentDefaultsAndRawDescriptionHelpFormatter, allow_abbrev=True)
    add_version_option(parser, VERSION)

    parser.add_argument(
        '--config', metavar='PATH', type=pathlib.Path, default=DEFAULT_CONFIG_PATH,
        help='''path to the configuration file;
        can be absolute, or relative to current woking directory''')
    parser.add_argument(
        '--daemon', '-d', action='store_true', default=False, required=False,
        help='''run as daemon''')

    add_verbosity_group(parser)

    return parser.parse_args(args)


def main(args=None):
    """Command-line interface of maildaemon."""
    colorama.init()

    parsed_args = parse_args(args)

    level = get_logging_level(parsed_args)
    root_log = logging.getLogger()
    _LOG.debug('setting root logger logging level to %i', level)
    root_log.setLevel(level)
    assert level in {root_log.getEffectiveLevel(), logging.NOTSET}, \
        (level, root_log.getEffectiveLevel())

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
