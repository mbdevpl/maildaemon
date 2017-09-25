"""
This is "__main__.py" file of maildaemon module.
"""

import argparse
import logging

import daemon

from ._version import VERSION as version
from .config import DEFAULT_CONFIG_PATH, load_config
from .connection_group import ConnectionGroup
from .message_filter import MessageFilter
from .daemon_group import DaemonGroup

_LOG = logging.getLogger(__name__)

class Formatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass

def parse_args():

    parser = argparse.ArgumentParser(
        prog='maildaemon',
        description='''maildaemon: multi-server mail filtering daemon supporting IMAP, POP and SMTP.

Configuration is stored in "{}".

'''.format(DEFAULT_CONFIG_PATH), epilog='''examples:
  maildaemon -h
  maildaemon -d

Copyright 2016 Mateusz Bysiek  http://mbdev.pl/
''',
        formatter_class=Formatter, allow_abbrev=True)
    """
    ArgumentParser(prog=None, usage=None, description=None, epilog=None, parents=[],
        formatter_class=argparse.HelpFormatter, prefix_chars='-', fromfile_prefix_chars=None,
        argument_default=None, conflict_handler='error', add_help=True, allow_abbrev=True)

    prog - The name of the program (default: sys.argv[0])
    usage - The string describing the program usage (default: generated from arguments added to
        parser)
    description - Text to display before the argument help (default: none)
    epilog - Text to display after the argument help (default: none)
    parents - A list of ArgumentParser objects whose arguments should also be included
    formatter_class - A class for customizing the help output
    prefix_chars - The set of characters that prefix optional arguments (default: ‘-‘)
    fromfile_prefix_chars - The set of characters that prefix files from which additional arguments
        should be read (default: None)
    argument_default - The global default value for arguments (default: None)
    conflict_handler - The strategy for resolving conflicting optionals (usually unnecessary)
    add_help - Add a -h/–help option to the parser (default: True)
    allow_abbrev - Allows long options to be abbreviated if the abbreviation is unambiguous.
        (default: True)

    formatter classes:
        class argparse.RawDescriptionHelpFormatter
        class argparse.RawTextHelpFormatter
        class argparse.ArgumentDefaultsHelpFormatter
        class argparse.MetavarTypeHelpFormatter

    add_argument(name or flags...[, action][, nargs][, const][, default][, type][, choices]
        [, required][, help][, metavar][, dest])

    name or flags - Either a name or a list of option strings, e.g. foo or -f, --foo.
    action - The basic type of action to be taken when this argument is encountered at the command
        line.
    nargs - The number of command-line arguments that should be consumed.
    const - A constant value required by some action and nargs selections.
    default - The value produced if the argument is absent from the command line.
    type - The type to which the command-line argument should be converted.
    choices - A container of the allowable values for the argument.
    required - Whether or not the command-line option may be omitted (optionals only).
    help - A brief description of what the argument does.
    metavar - A name for the argument in usage messages.
    dest - The name of the attribute to be added to the object returned by parse_args().

    action:
        'store', 'store_const', 'store_true', 'store_false', 'append', 'append_const', 'count',
        'help', 'version'
    nargs:
        N, '?', '*', '+'
    """

    parser.version = version

    """
    parser.add_argument(
        'command', default=None, type=str, choices=[n for _, n, __ in commands],
        help='''a command that can be one of: {}'''
        .format('; '.join(['"{}" - {}'.format(n, d) for _, n, d in commands]))
        )

    parser.add_argument(
        'path', nargs='+', default=None, type=str,
        help='''path(s) to file(s) or folder(s) to be processed; if "--from-language" is not given,
        all files found in given path(s) that can be processed will be processed;
        if "--from-language" is given, only source files that are in given language will be
        processed''')

    parser.add_argument(
        '--recursive', '-r', action='store_true', default=False, required=False,
        help='''if folder path is encountered, scan it recursively''')

    parser.add_argument(
        '--output-path', '--out', '-o', action='append', default=None, type=str, required=False,
        help='''path to output file or folder''')

    parser.add_argument(
        '--from-language', '--from', default=None, type=str, choices=langs.keys(), required=False,
        help='''programming language of source file(s)''')
    #, case-insensitive prefix matching resolves
    #    given value to the first matching language

    parser.add_argument(
        '--to-language', '--to', default=None, type=str, choices=langs.keys(), required=False,
        help='''programming language of target file(s), prefix matching is used here as well''')
    """

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

    return parser.parse_args()

def main():

    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    if args.quiet:
        logging.getLogger().setLevel(logging.CRITICAL)

    config = load_config()

    group = ConnectionGroup.from_dict(config['connections'])

    filters = []
    for _, filter_data in config['filters'].items():
        flt = MessageFilter.from_dict(filter_data, group.named_connections)
        filters.append(flt)

    daemon_group = DaemonGroup(group, filters)

    if args.daemon:
        with daemon.DaemonContext():
            daemon_group.run()
    else:
        daemon_group.run()

if __name__ == '__main__':
    main()
