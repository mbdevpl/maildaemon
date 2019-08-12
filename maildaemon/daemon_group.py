
import logging
import time
import typing as t

import timing

# from .message import Message
# from .message_filter import MessageFilter
from .connection_group import ConnectionGroup
from .daemon import Daemon

_LOG = logging.getLogger(__name__)
_TIME = timing.get_timing_group(__name__)


class DaemonGroup:

    """Manage a group of mail daemons."""

    def __init__(
            self, connections: ConnectionGroup, filters: 't.Sequence[MessageFilter]',
            max_iterations: int = 1):
        self._connections = connections
        self._daemons = []
        for daemon in connections:
            if isinstance(daemon, Daemon):
                self._daemons.append(daemon)
        self._filters = []
        for filter_ in filters:
            self._filters.append(filter_)
        self.max_iterations = max_iterations

    # def add_filter(self, message_filter: 'MessageFilter'):
    #    self._filters.append(message_filter)

    def update(self):
        for daemon in self._daemons:
            _LOG.warning('updating %s', daemon)
            daemon.update()

    def run(self):
        self._connections.connect_all()

        iteration = 0
        while True:
            iteration += 1
            self._connections.purge_dead()
            if not self._connections:
                _LOG.warning('all connections died')
                break

            _LOG.warning('iteration %i: %i active connection(s)', iteration, len(self._connections))

            with _TIME.measure('DaemonGroup.run.iteration.update') as timer:
                self.update()

            if iteration >= self.max_iterations:
                break

            # print('processing {} new messages: {}'.format(len(new_msg_ids), new_msg_ids))

            if timer.elapsed < 4:
                time.sleep(4 - timer.elapsed)

        self._connections.disconnect_all()

    def __len__(self):
        return len(self._connections)
