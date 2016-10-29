
import logging
import time
#import typing as t

#from .message import Message
#from .message_filter import MessageFilter
from .connection_group import ConnectionGroup
from .daemon import Daemon
#from .timing import Timing

_LOG = logging.getLogger(__name__)

class DaemonGroup:

    def __init__(self, connections: ConnectionGroup, filters: 't.Sequence[MessageFilter]'):

        self._connections = connections

        self._daemons = []
        for daemon in connections:
            if isinstance(daemon, Daemon):
                self._daemons.append(daemon)

        self._filters = []
        for filter_ in filters:
            self._filters.append(filter_)

    #def add_filter(self, message_filter: 'MessageFilter'):

    #    self._filters.append(message_filter)

    def update(self):

        for daemon in self._daemons:
            daemon.update()

    def run(self):

        self._connections.connect_all()

        #while True:
        for _ in range(0, 3):

            #_T1 = Timing('is_alive').start()
            self._connections.purge_dead()
            if len(self._connections) == 0:
                break
            #_T1.stop()

            #_T2 = Timing('update').start()
            self.update()
            #_T2.stop()

            #print('processing {} new messages: {}'.format(len(new_msg_ids), new_msg_ids))

            #_LOG.debug('%s %s', _T1, _T2)
            time.sleep(5)

        self._connections.disconnect_all()
