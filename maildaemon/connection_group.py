
from .connection import Connection

class ConnectionGroup(Connection):

    def __init__(self, *connections):

        self._connections = []
        for connection in connections:
            self._connections.append(connection)

    def connect(self) -> None:

        for connection in self._connections:
            connection.connect()

    def is_alive(self) -> bool:

        all_alive = True

        for connection in self._connections:
            is_alive = connection.is_alive()
            all_alive = all_alive and is_alive

        return all_alive

    def disconnect(self) -> None:

        for connection in self._connections:
            connection.disconnect()
