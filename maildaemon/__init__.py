"""
This is "__init__.py" file of maildaemon module.
"""

import logging
import logging.config

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'brief': {'style': '{', 'format': '{name} [{levelname}] {message}'},
        'precise': {'style': '{', 'format': '{asctime} {name} [{levelname}] {message}'}
        },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler', 'formatter': 'brief', 'level': logging.NOTSET,
            'stream': 'ext://sys.stdout'}
        },
    'root': {'level': logging.DEBUG, 'handlers': ['console']}
    })

from .config import load_config

#from .connection import Connection
#from .connection_group import ConnectionGroup
#from .imap_connection import IMAPConnection
#from .smtp_connection import SMTPConnection
#from .pop_connection import POPConnection

#from .message import Message
#from .message_filter import MessageFilter

#from .daemon import Daemon
#from .daemon_group import DaemonGroup
from .imap_daemon import IMAPDaemon
from .smtp_daemon import SMTPDaemon
from .pop_daemon import POPDaemon

#from .gmail_imap_daemon import GmailIMAPDaemon
