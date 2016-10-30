
import unittest

from maildaemon.config import load_config
from maildaemon.imap_daemon import IMAPDaemon
from maildaemon.message_filter import MessageFilter

class Test(unittest.TestCase):

    config = load_config()

    @unittest.skip('temporary')
    def test_apply(self):

        c = IMAPDaemon.from_dict(self.config['connections']['gmail-imap'])

        c.connect()

        msg = c.retrieve_message(1)

        f = MessageFilter.from_dict(self.config['filters']['facebook'], {'gmail-imap': c})
        result = f.applies_to(msg)
        self.assertIsInstance(result, bool, msg=(f, msg))

        c.disconnect()
