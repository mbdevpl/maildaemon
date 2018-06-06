"""Handling e-mail messages."""

import datetime
import email.header
import email.message
import logging

import dateutil.parser

from .connection import Connection

_LOG = logging.getLogger(__name__)


def recode_header(raw_data) -> str:
    return email.header.make_header(email.header.decode_header(raw_data))


def is_name_and_address(text) -> bool:
    return '<' in text and '>' in text


def split_name_and_address(text) -> tuple:
    if is_name_and_address(text):
        begin = text.rfind('<')
        end = text.rfind('>')
        assert begin < end
        return text[begin + 1:end], text[:begin]
    return text, None


def recode_timezone_info(dt: datetime.datetime):

    name = dt.tzname()
    dst = dt.dst()
    dst = (' ' + dst) if dst != datetime.timedelta() else ''

    if name == 'UTC':
        return '{}{}'.format(name, dst)

    offset = dt.utcoffset()
    offset = ('+' if offset >= datetime.timedelta() else '') + str(offset.total_seconds() / 3600)

    if name is None or len(name) == 0:
        return 'UTC{}{}'.format(offset, dst)

    return '{} (UTC{}{})'.format(name, offset, dst)


class Message:

    """An e-mail message."""

    @classmethod
    def from_email_message(cls, msg: email.message.EmailMessage, server: Connection = None,
                           folder: str = None, msg_id: int = None):

        m = cls(msg, server, folder, msg_id)

        for key, value in msg.items():
            if key == 'From':
                m.from_address, m.from_name = split_name_and_address(str(recode_header(value)))
            elif key == 'Reply-To':
                m.reply_to_address, m.reply_to_name = split_name_and_address(
                    str(recode_header(value)))
            elif key == 'To':
                m.to_address, m.to_name = split_name_and_address(str(recode_header(value)))
            elif key == 'Subject':
                m.subject = recode_header(value)
            elif key == 'Date':
                _datetime = dateutil.parser.parse(value)  # type: datetime.datetime
                m.datetime = _datetime
                m.timezone = recode_timezone_info(_datetime)
            elif key == 'Received':
                m.received.append(value)
            elif key == 'Return-Path':
                m.return_path = value
            elif key == 'Envelope-To':
                m.envelope_to = value
            elif key == 'Message-Id':
                m.message_id = value
            elif key == 'Content-Type':
                m.content_type = value
            else:
                m.other_headers.append((key, value))

        _parts = msg.get_payload() if msg.is_multipart() else [msg]
        for part in _parts:
            content_type = part.get_content_type()
            if content_type not in {'text/plain', 'text/html'}:
                _LOG.info('treating message part with type %s as attachment', content_type)
                m.attachments.append(part)
                continue
            charset = part.get_content_charset()
            if not charset:
                _LOG.error('no content charset in a message %s in part %s',
                           m.str_headers_compact(), part[:128])
                m.attachments.append(part)
                continue
            text = part.get_payload(decode=True).decode(charset)
            m.contents.append(text)
        return m

    def __init__(self, msg=None, server=None, folder=None, msg_id=None):

        self._email_message = msg  # type: email.message.EmailMessage
        self._origin_server = server  # type: Connection
        self._origin_folder = folder  # type: str
        self._origin_id = msg_id  # type: int

        self.from_address = None
        self.from_name = None
        self.reply_to_address = None
        self.reply_to_name = None
        self.to_address = None
        self.to_name = None
        self.subject = None
        self.datetime = None
        self.timezone = None
        self.local_date = None
        self.local_time = None

        self.received = []
        self.return_path = None
        self.envelope_to = None
        self.message_id = None
        self.content_type = None
        self.other_headers = []

        self.contents = []
        self.attachments = []

    @property
    def date(self):
        return self.datetime.date()

    @property
    def time(self):
        return self.datetime.time()

    def move_to(self, server: Connection, folder: str) -> None:
        """Move message to a specific folder on a specific server."""
        if server is self._origin_server:
            if folder == self._origin_folder:
                _LOG.debug('move_to() destination same as origin, nothing to do')
            _LOG.error('move_to() not implemented moving within same server')
            raise NotImplementedError()
        else:
            _LOG.error('move_to() not implemented moving between servers')
            raise NotImplementedError()

    def copy_to(self, server: Connection, folder: str) -> None:
        raise NotImplementedError()

    def send_via(self, server: Connection) -> None:
        server.send_message(self._email_message)

    def str_headers(self):
        return '\n'.join([
            'From:     {}'.format(self.from_address),
            '          {}'.format(self.from_name),
            'Reply-To: {}'.format(self.reply_to_address),
            '          {}'.format(self.reply_to_name),
            'To:       {}'.format(self.to_address),
            '          {}'.format(self.to_name),
            'Subject:  {}'.format(self.subject),
            'Date:     {}'.format(self.date),
            'Time:     {}'.format(self.time),
            'Timezone: {}'.format(self.timezone),
            'Locally:  {}'.format(self.local_date),
            '          {}'.format(self.local_time),
            # '',
            # '  Received: {}'.format(self.received),
            # '  Return-Path: {}'.format(self.return_path),
            # '  Envelope-To: {}'.format(self.envelope_to),
            # '  Message-Id: {}'.format(self.message_id),
            # '  Content-Type: {}'.format(self.content_type),
            # 'Other headers:',
            # '\n'.join(['  {}: {}'.format(k, v) for k, v in self.other_headers]),
            ])

    def str_headers_compact(self):
        return '\n'.join([
            'From:     {} {}'.format(self.from_address, self.from_name),
            'Reply-To: {} {}'.format(self.reply_to_address, self.reply_to_name),
            'To:       {} {}'.format(self.to_address, self.to_name),
            'Subject:  {}'.format(self.subject),
            'Datetime: {} {} {}'.format(self.date, self.time, self.timezone)
            ])

    def str_quote(self):
        raise NotImplementedError()

    def str_forward(self):
        raise NotImplementedError()

    def str_complete(self):
        return '\n'.join([
            self.str_headers(),
            '',
            'Contents{}:'.format(' (multipart, {} parts)'.format(len(self.contents))
                                 if len(self.contents) > 1 else ''),
            80*'=',
            (80*'=' + '\n').join(self.contents),
            80*'=',
            ])

    def __str__(self):
        return self.str_complete()

    def __repr__(self):
        return self.str_headers_compact()
