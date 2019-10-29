"""Actions for MessageFilter class."""

from .connection import Connection

from .message import Message
# from .folder import Folder


def mark(message: Message, connection: Connection, status: str):
    """Mark given message."""
    if status == 'read':
        # TODO: replace with message.set_flag(flag) after it's implemented
        return connection.add_messages_flags([message._origin_id], ['Seen'])

    raise NotImplementedError(status)


def move(message: Message, connection: Connection, folder_name: str):
    """Move given message to a given location."""
    return message.move_to(connection, folder_name)
