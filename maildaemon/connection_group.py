
import logging

#from .connection import Connection

_LOG = logging.getLogger(__name__)

class ConnectionGroup:

    def __init__(self, *connections):

        self._connections = []
        for connection in connections:
            self._connections.append(connection)

    def connect(self) -> None:

        _LOG.info('establishing %i connections...', len(self))

        for connection in self._connections:
            connection.connect()

    def is_alive(self) -> bool:

        all_alive = True

        for connection in self._connections:
            is_alive = connection.is_alive()
            all_alive = all_alive and is_alive

        return all_alive

    def disconnect(self) -> None:

        _LOG.info('ending %i connections...', len(self))

        for connection in self._connections:
            connection.disconnect()

    def __len__(self):
        return len(self._connections)

    def __iter__(self):
        return iter(self._connections)
