
import logging
import typing as t

import ordered_set

from .connection import Connection
from .imap_cache import IMAPCache
from .smtp_connection import SMTPConnection
from .pop_cache import POPCache

_LOG = logging.getLogger(__name__)


class ConnectionGroup(t.Dict[str, Connection]):

    """Group of connections."""

    @classmethod
    def from_dict(cls, data: dict) -> 'ConnectionGroup':

        connections = {}
        for name, entry in data.items():
            try:
                connection_class = {
                    'IMAP': IMAPCache,
                    'SMTP': SMTPConnection,
                    'POP': POPCache
                    }[entry['protocol']]
            except KeyError:
                # _LOG.exception('invalid protocol: "%s"', data['protocol'])
                continue

            try:
                connection = connection_class.from_dict(entry)
            except:
                _LOG.exception('failed to construct connection object for "%s" with parameters: %s',
                               name, entry)
                continue

            connections[name] = connection

        group = cls(**connections)
        return group

    def __init__(self, **connections):
        super().__init__(**connections)
        self._connections = {}
        for name, connection in connections.items():
            self._connections[name] = connection

    @property
    def connections(self):
        return self._connections

    def connect_all(self) -> None:
        _LOG.info('establishing %i connections...', len(self))
        for _, connection in self._connections.items():
            connection.connect()

    @property
    def alive_connections(self) -> t.List[Connection]:
        """List of connections that are alive at the moment."""
        alive_connections = []
        for name, connection in self._connections.items():
            if connection.is_alive():
                alive_connections.append(name)
        return alive_connections

    @property
    def dead_connections(self):
        return list(ordered_set.OrderedSet(self.connections)
                    - ordered_set.OrderedSet(self.alive_connections))

    def purge_dead(self) -> None:
        """Check connections one by one and remove dead ones."""
        for name in self.dead_connections:
            _LOG.info('purging lost connection with %s', name)
            del self._connections[name]

        if not self._connections:
            _LOG.info('purged all connections')

    def disconnect_all(self) -> None:
        _LOG.info('ending %i connections...', len(self))
        for _, connection in self._connections.items():
            connection.disconnect()

    def __len__(self):
        return len(self._connections)

    def __iter__(self):
        return iter(self._connections)
