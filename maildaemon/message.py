"""Handling e-mail messages."""

import datetime
import email.header
import email.message
import logging
import typing as t

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

    if name is None or not name:
        return 'UTC{}{}'.format(offset, dst)

    return '{} (UTC{}{})'.format(name, offset, dst)


class Message:
    """An e-mail message."""

    def __init__(self, msg: email.message.EmailMessage = None, server: Connection = None,
                 folder: str = None, msg_id: int = None):
        assert folder is None or isinstance(folder, str), type(folder)
        assert msg_id is None or isinstance(msg_id, int), type(msg_id)

        self._email_message = msg  # type: email.message.EmailMessage
        self._origin_server = server  # type: Connection
        self._origin_folder = folder  # type: str
        self._origin_id = msg_id  # type: int

        self.from_address = None  # type: str
        self.from_name = None  # type: str
        self.reply_to_address = None  # type: str
        self.reply_to_name = None  # type: str
        self.to_address = None  # type: str
        self.to_name = None  # type: str
        self.subject = None  # type: str
        self.datetime = None  # type: datetime.datetime
        self.timezone = None
        self.local_date = None
        self.local_time = None

        self.received = []
        self.return_path = None
        self.envelope_to = None
        self.message_id = None
        self.content_type = None
        self.other_headers = []

        self.flags = set()  # type: t.Set[str]
        self.contents = []
        self.attachments = []

        if msg is not None:
            self._init_headers_from_email_message(msg)
            self._init_contents_from_email_message(msg)

    @property
    def date(self) -> datetime.date:
        if self.datetime is None:
            return None
        return self.datetime.date()

    @property
    def time(self) -> datetime.time:
        if self.datetime is None:
            return None
        return self.datetime.time()

    @property
    def is_read(self) -> bool:
        return 'Seen' in self.flags

    @property
    def is_unread(self) -> bool:
        return not self.is_read()

    @property
    def is_answered(self) -> bool:
        return 'Answered' in self.flags

    @property
    def is_flagged(self) -> bool:
        return 'Flagged' in self.flags

    def _init_headers_from_email_message(self, msg: email.message.EmailMessage) -> None:
        for key, value in msg.items():
            self._init_header_from_keyvalue(key, value)

    def _init_header_from_keyvalue(self, key: str, value: str) -> None:
        if key == 'From':
            self.from_address, self.from_name = split_name_and_address(str(recode_header(value)))
        elif key == 'Reply-To':
            self.reply_to_address, self.reply_to_name = split_name_and_address(
                str(recode_header(value)))
        elif key == 'To':
            self.to_address, self.to_name = split_name_and_address(str(recode_header(value)))
        elif key == 'Subject':
            self.subject = str(recode_header(value))
        elif key == 'Date':
            try:
                _datetime = dateutil.parser.parse(value)  # type: datetime.datetime
                self.datetime = _datetime
                self.timezone = recode_timezone_info(_datetime)
            except ValueError:
                _LOG.exception('dateutil failed to parse string "%s" into a date/time', value)
        elif key == 'Received':
            self.received.append(value)
        elif key == 'Return-Path':
            self.return_path = value
        elif key == 'Envelope-To':
            self.envelope_to = value
        elif key == 'Message-Id':
            self.message_id = value
        elif key == 'Content-Type':
            self.content_type = value
        else:
            self.other_headers.append((key, value))

    def _init_contents_from_email_message(self, msg: email.message.EmailMessage) -> None:
        if not msg.get_payload():
            return
        if msg.get_content_maintype() != 'multipart':
            self._init_contents_part(msg)
            return
        content_type = msg.get_content_type()
        parts = msg.get_payload()
        if isinstance(parts, str):
            _LOG.error('one of %i parts in a message is %s, but it has no subparts',
                       len(parts), content_type)
            assert not parts, parts
            return
        assert isinstance(parts, list), type(parts)
        assert parts
        if content_type == 'multipart/alternative':
            if len(parts) > 1:
                _LOG.warning('taking last alternative of %i available in part type %s'
                             ' - ignoring others', len(parts), content_type)
            self._init_contents_from_email_message(parts[-1])
        elif content_type == 'multipart/related':
            if len(parts) > 1:
                _LOG.warning('taking only first part of %i available in part type %s'
                             ' - ignoring related parts', len(parts), content_type)
            self._init_contents_from_email_message(parts[0])
        elif content_type == 'multipart/mixed':
            for part in parts:
                self._init_contents_from_email_message(part)
        else:
            raise NotImplementedError(
                'handling of "{}" not implemented'.format(content_type))

    def _init_contents_part(self, part: email.message.Message):
        content_type = part.get_content_type()
        if content_type not in {'text/plain', 'text/html'}:
            _LOG.info('treating message part with type %s as attachment', content_type)
            self.attachments.append(part)
            return
        charset = part.get_content_charset()
        if charset:
            text = part.get_payload(decode=True)
            try:
                text = text.decode(charset)
            except UnicodeDecodeError:
                _LOG.exception('failed to decode %i-character text using encoding "%s"',
                               len(text), charset)
        else:
            text = part.get_payload()
            try:
                if isinstance(text, bytes):
                    text = text.decode('utf-8')
            except UnicodeDecodeError:
                _LOG.exception('failed to decode %i-character text using encoding "%s"',
                               len(text), 'utf-8')
            if not isinstance(text, str):
                _LOG.error('no content charset in a message %s in part %s -- attachment?',
                           self.str_headers_compact(), part.as_bytes()[:128])
                self.attachments.append(part)
                text = None
        if not text:
            return
        self.contents.append(text)

    def move_to(self, server: Connection, folder_name: str) -> None:
        """Move message to a specific folder on a specific server."""
        if server is not self._origin_server:
            raise NotImplementedError('move_to() not implemented moving between servers')
        if folder_name == self._origin_folder:
            _LOG.debug('move_to() destination same as origin, nothing to do')
            return
        from .imap_connection import IMAPConnection
        assert isinstance(server, IMAPConnection), type(server)
        server.move_messages([self._origin_id], folder_name, self._origin_folder)

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
            'id: {}'.format(self._origin_id),
            'flags: {}'.format(self.flags),
            '',
            'contents{}:'.format(' (multipart, {} parts)'.format(len(self.contents))
                                 if len(self.contents) > 1 else ''),
            80*'=',
            (80*'=' + '\n').join(self.contents),
            80*'=',
            ])

    def __str__(self):
        return self.str_complete()

    def __repr__(self):
        return self.str_headers_compact()
