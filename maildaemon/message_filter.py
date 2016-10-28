
import functools
import logging
import operator
import re
import typing as t

from .message import Message
from .connection import Connection

_LOG = logging.getLogger(__name__)

OPERATORS = {
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

 - key is a 1- or 2-character string representation of a predicate on string variable.
 
 - value is a 1-argument function that creates another 1-argument function (a said predicate)

Every operator is meant to create and return one-argument function that applies a predicate
on its argument.
"""

class MessageFilter:

    @classmethod
    def from_dict(
            cls, data: dict, named_connections: t.Mapping[str, Connection]={}) -> 'MessageFilter':

        connections = []
        for connection_name in data['connections']:
            connection = named_connections[connection_name]
            connections.append(connection)

        condition = []
        if len(data['condition']) > 1:
            _LOG.debug('[')
        for i, disjunct in enumerate(data['condition']):
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
                    op_function = OPERATORS[operator_](arg)
                except KeyError:
                    operator_ = operator_and_arg[:1]
                    arg = operator_and_arg[1:]
                    try:
                        op_function = OPERATORS[operator_](arg)
                    except KeyError as err:
                        raise RuntimeError() from err
                _LOG.info(
                    'parsed to e-mail variable: "%s", operator: %s, argument: "%s" (mapped to %s)',
                    variable, operator_, arg, op_function)
                conjunction.append((variable, op_function))
            condition.append(conjunction)
            if len(disjunct) > 1:
                _LOG.debug(')')
        if len(data['condition']) > 1:
            _LOG.debug(']')

        #print(data)
        #print(named_connections)

        actions = []

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
