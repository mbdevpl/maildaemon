
import logging

#from .connection import Connection
from .imap_daemon import IMAPDaemon
from .smtp_connection import SMTPConnection
from .pop_daemon import POPDaemon

_LOG = logging.getLogger(__name__)

class ConnectionGroup:

    @classmethod
    def from_dict(cls, data: dict) -> 'ConnectionGroup':

        connections = []
        names = []
        for name, data in data.items():
            try:
                connection_class = {
                    'IMAP': IMAPDaemon,
                    'SMTP': SMTPConnection,
                    'POP': POPDaemon
                    }[data['protocol']]
            except KeyError:
                #_LOG.exception('invalid protocol: "%s"', data['protocol'])
                continue

            try:
                connection = connection_class.from_dict(data)
            except:
                _LOG.exception(
                    'failed to construct connection object for "%s" with parameters: %s', name, data)
                continue

            connections.append(connection)
            names.append(name)

        group = cls(*connections)
        group._names = names

        return group

    def __init__(self, *connections):

        self._connections = []
        for connection in connections:
            self._connections.append(connection)

        self._names = None
        self._named_connections = None

    @property
    def named_connections(self):

        if self._named_connections is None:
            self._named_connections = {k: v for k, v in zip(self._names, self._connections)}

        return self._named_connections

    def connect_all(self) -> None:

        _LOG.info('establishing %i connections...', len(self))

        for connection in self._connections:
            connection.connect()

    def all_alive(self) -> bool:

        all_alive = True

        for connection in self._connections:
            is_alive = connection.is_alive()
            all_alive = all_alive and is_alive

        return all_alive

    def purge_dead(self) -> None:
        """
        Check connections one by one and remove dead ones.
        """

        dead_connections = []
        for i, connection in enumerate(self._connections):
            if not connection.is_alive():
                dead_connections.append(i)
                _LOG.info('lost connection with %s', connection)

        for i in reversed(dead_connections):
            del self._connections[i]

        if len(self._connections) == 0:
            _LOG.warning('lost all connections')

    def disconnect_all(self) -> None:

        _LOG.info('ending %i connections...', len(self))

        for connection in self._connections:
            connection.disconnect()

    def __len__(self):
        return len(self._connections)

    def __iter__(self):
        return iter(self._connections)
