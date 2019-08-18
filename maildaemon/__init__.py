"""This is "__init__.py" file of maildaemon module."""

from ._logging import configure_logging

# from .config import load_config

from .connection import Connection
# from .connection_group import ConnectionGroup
from .imap_connection import IMAPConnection
# from .smtp_connection import SMTPConnection
# from .pop_connection import POPConnection

from .message import Message
# from .message_filter import MessageFilter

from .folder import Folder

# from .daemon import Daemon
# from .daemon_group import DaemonGroup
# from .imap_daemon import IMAPDaemon
# from .smtp_daemon import SMTPDaemon
# from .pop_daemon import POPDaemon

# from .gmail_imap_daemon import GmailIMAPDaemon

__all__ = ['Connection', 'IMAPConnection', 'Message', 'Folder']

configure_logging()
