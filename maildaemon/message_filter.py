
import functools
import logging
import operator
import re
import typing as t

from .message import Message
from .connection import Connection

_LOG = logging.getLogger(__name__)

CONDITION_OPERATORS = {
    #'>': lambda arg: functools.partial(),
    '=': lambda arg: functools.partial(operator.eq, arg),
    #'!=': lambda a, b: a != b,
    '=~': lambda arg: re.compile(arg).fullmatch,
    '~<': lambda arg: functools.partialmethod(str.startswith, prefix=arg),
    '~': lambda arg: functools.partial(operator.contains, b=arg),
    #'~!': lambda a, b: a not in b,
    '~~': lambda arg: re.compile(arg).find,
    '~>': lambda arg: lambda variable: variable.endswith(arg),
    }
"""
Define a mapping: str -> t.Callable[[str], t.Callable[[str], bool]].

In such mapping:

 - key is a 1- or 2-character string representation of a predicate on string variable; and
 
 - value is a 1-argument function that creates another 1-argument function (a said predicate).

Every operator is meant to create and return one-argument function that applies a predicate
on its argument.
"""

ACTIONS = {
    'mark': lambda message, imap_daemon, flag: imap_daemon.set_flag(message, flag),
    'move': lambda message, imap_daemon, folder: imap_daemon.move_message(message, folder),
    'copy': lambda message, imap_daemon, folder: imap_daemon.copy_message(message, folder),
    'delete': None,
    'reply': None,
    'forward': lambda message, smtp_daemon, address:  smtp_daemon.forward_message(message, address)
    }
"""
Define a mapping: str -> t.Callable[[Message], None].

In such mapping:

 - key is a string representation of an operation on Message instance; and

 - value is a function which takes Message instance and possibly other arguments, and executes
   said operation.

Every action is meant to create and return one-argument function that performs an operation
involving a and possibly other entities.
"""

class MessageFilter:

    @classmethod
    def from_dict(
            cls, data: dict, named_connections: t.Mapping[str, Connection]={}) -> 'MessageFilter':

        try:
            connection_names = data['connections']
        except KeyError:
            connection_names = []

        connections = []
        for connection_name in connection_names:
            connection = named_connections[connection_name]
            connections.append(connection)

        try:
            disjunction = data['condition']
        except KeyError:
            disjunction = []

        condition = []
        if len(disjunction) > 1:
            _LOG.debug('[')
        for i, disjunct in enumerate(disjunction):
            if i > 0:
                _LOG.debug('] or [')
            if len(disjunct) > 1:
                _LOG.debug('(')
            conjunction = []
            for j, conjunct in enumerate(disjunct):
                if j > 0:
                    _LOG.debug(') and (')
                _LOG.debug('parsing expression: %s', conjunct)
                variable, _, operator_and_arg = conjunct.partition(':')
                operator_ = operator_and_arg[:2]
                arg = operator_and_arg[2:]
                try:
                    op_function = CONDITION_OPERATORS[operator_](arg)
                except KeyError:
                    operator_ = operator_and_arg[:1]
                    arg = operator_and_arg[1:]
                    try:
                        op_function = CONDITION_OPERATORS[operator_](arg)
                    except KeyError as err:
                        raise RuntimeError() from err
                _LOG.debug(
                    'parsed to e-mail variable: "%s", operator: %s, argument: "%s" (mapped to %s)',
                    variable, operator_, arg, op_function)
                conjunction.append((variable, op_function))
            condition.append(conjunction)
            if len(disjunct) > 1:
                _LOG.debug(')')
        if len(disjunction) > 1:
            _LOG.debug(']')

        try:
            action_strings = data['actions']
        except KeyError:
            action_strings = []

        actions = []
        for action_string in action_strings:
            _LOG.debug('parsing action: %s', action_string)
            operation, _, args = action_string.partition(':')
            try:
                action = ACTIONS[operation]
            except KeyError as err:
                _LOG.exception('action "%s" consists of invalid operation "%s"', action_string, operation)
                raise RuntimeError('cannot construct the filter with invalid action')
            _LOG.debug('parsed to operation %s, args: %s (mapped to action %s)', operation, args, action)
            actions.append(action)

        return cls(connections, condition, actions)

    def __init__(
            self, connections: t.List[Connection],
            condition: t.List[t.List[t.Tuple[str, t.Callable[[str], bool]]]],
            actions: t.List[t.Callable[[t.Any], None]]):

        self._connections = connections
        self._condition = condition
        self._actions = actions

    def applies_to(self, message: Message) -> bool:

        for conjunction in self._condition:
            conjunction_satisfied = True
            for arg, predicate in conjunction:
                try:
                    attr_value = getattr(message, arg)
                except AttributeError:
                    _LOG.exception(
                        'cannot apply predicate %s in conjunction %s', predicate, conjunction)
                    conjunction_satisfied = False
                    break
                if not predicate(attr_value):
                    conjunction_satisfied = False
                    break
            if conjunction_satisfied:
                return True

        return False
