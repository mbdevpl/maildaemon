"""Filter that is applied on e-mail messages."""

import functools
import logging
import operator
import re
import typing as t

from .message import Message
from .connection import Connection
from .filter_actions import mark, move

_LOG = logging.getLogger(__name__)

CONDITION_OPERATORS = {
    # '>': lambda arg: functools.partial(),
    '=': lambda arg: functools.partial(operator.eq, arg),
    # '!=': lambda a, b: a != b,
    '=~': lambda arg: re.compile(arg).fullmatch,
    '~<': lambda arg: functools.partialmethod(str.startswith, prefix=arg),
    '~': lambda arg: functools.partial(operator.contains, b=arg),
    # '~!': lambda a, b: a not in b,
    '~~': lambda arg: re.compile(arg).find,
    '~>': lambda arg: lambda variable: variable.endswith(arg),
    }
"""Define a mapping: str -> t.Callable[[str], t.Callable[[str], bool]].

In such mapping:

 - key is a 1- or 2-character string representation of a predicate on string variable; and

 - value is a 1-argument function that creates another 1-argument function (a said predicate).

Every operator is meant to create and return one-argument function that applies a predicate
on its argument.
"""

ACTIONS = {
    'mark': mark,
    'move': move,
    'copy': lambda message, imap_daemon, folder: imap_daemon.copy_message(message, folder),
    'delete': None,
    'reply': None,
    'forward': lambda message, smtp_daemon, address: smtp_daemon.forward_message(message, address)}
"""Define a mapping: str -> t.Callable[[Message], None].

In such mapping:

 - key is a string representation of an operation on Message instance; and

 - value is a function which takes Message instance and possibly other arguments, and executes
   said operation.

Every action is meant to create and return one-argument function that performs an operation
involving a and possibly other entities.
"""

FILTER_CODE = 'lambda message: {}'


class MessageFilter:
    """For selective actions on messages."""

    @classmethod
    def from_dict(cls, data: dict,
                  named_connections: t.Mapping[str, Connection] = {}) -> 'MessageFilter':
        try:
            connection_names = data['connections']
        except KeyError:
            connection_names = []

        connections = []
        for connection_name in connection_names:
            connections.append(named_connections[connection_name])

        condition = eval(FILTER_CODE.format(data['condition']))

        try:
            action_strings = data['actions']
        except KeyError:
            action_strings = []

        actions = []
        for action_string in action_strings:
            _LOG.debug('parsing action: %s', action_string)
            operation, _, raw_args = action_string.partition(':')
            try:
                action = ACTIONS[operation]
            except KeyError:
                _LOG.exception('action "%s" consists of invalid operation "%s"',
                               action_string, operation)
                raise RuntimeError('cannot construct the filter with invalid action')
            if action is move:
                connection, _, folder = raw_args.partition('/')
                args = (named_connections[connection], folder)
            elif action is mark:
                args = (raw_args,)
            else:
                raise NotImplementedError(
                    f'parsing args "{raw_args}" for action "{operation}" is not implemented yet')
            _LOG.debug('parsed to operation %s (mapped to action %s), args: %s',
                       operation, action, args)
            actions.append((action, args))

        return cls(connections, condition, actions)

    def __init__(
            self, connections: t.List[Connection],
            condition: t.List[t.List[t.Tuple[str, t.Callable[[str], bool]]]],
            actions: t.List[t.Tuple[t.Callable[[t.Any], None], t.Sequence[t.Any]]]):
        self._connections = connections
        self._condition = condition
        self._actions = actions

    def applies_to(self, message: Message) -> bool:
        try:
            return self._condition(message)
        except:
            _LOG.exception('filter %s failed on message %s', self, message)
            return False

    def apply_unconditionally(self, message: Message):
        """Apply actions of this filter to the given message ignoring the conditions."""
        for action, args in self._actions:
            if action not in {move, mark}:
                raise RuntimeError('refusing to execute untested action')
            if action is mark:
                args = (message._origin_server, *args)
            action(message, *args)

    def apply_to(self, message: Message):
        """Apply filter on the message if it satisfies the filter conditions."""
        if self.applies_to(message):
            self.apply_unconditionally(message)

    def __str__(self):
        return str({
            'connections': self._connections,
            'condition': self._condition,
            'actions': [
                '{}(message, {})'.format(action.__name__, ', '.join([str(arg) for arg in args]))
                for action, args in self._actions]})
