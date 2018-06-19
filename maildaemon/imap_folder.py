
import logging

_LOG = logging.getLogger(__name__)


class IMAPFolder(list):

    """For storing messages.

    Extends the list in order to store messages.
    """

    def __init__(self, *args, name: str, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = name
        self._subfolders = set()
        self._flags = []
