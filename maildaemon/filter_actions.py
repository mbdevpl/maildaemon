"""Actions for MessageFilter class."""

from .connection import Connection

from .message import Message
# from .folder import Folder


def move(message: Message, connection: Connection, folder_name: str):
    """Move given message to a given location."""
    return message.move_to(connection, folder_name)
