"""Handling e-mail messages."""

import datetime
import email.header
import email.message
import logging
import typing as t

import dateutil.parser

from .connection import Connection

_LOG = logging.getLogger(__name__)


def recode_header(raw_data: t.Union[bytes, str]) -> str:
    """Normalize the header value."""
    decoded_data = email.header.decode_header(raw_data)
    try:
        return email.header.make_header(decoded_data)
    except UnicodeDecodeError as err:
        try:
            return email.header.make_header([(decoded_data[0][0], 'utf-8')])
        except:
            _LOG.exception('both "%s" and "utf-8" fail to decode the header', decoded_data[0][1])
        raise ValueError(f'after decoding {raw_data!r}, obtained {decoded_data!r}'
                         ' which cannot be re-made into a header') from err


def is_name_and_address(text: str) -> bool:
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
        return f'{name}{dst}'

    offset = dt.utcoffset()
    offset = ('+' if offset >= datetime.timedelta() else '') + str(offset.total_seconds() / 3600)

    if name is None or not name:
        return f'UTC{offset}{dst}'

    return f'{name} (UTC{offset}{dst})'


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

    @property
    def is_deleted(self) -> bool:
        return 'Deleted' in self.flags

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
            self._init_datetime_from_header_value(value)
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

    def _init_datetime_from_header_value(self, value: str):
        self.datetime = None
        try:
            self.datetime = dateutil.parser.parse(value)
        except ValueError:
            try:
                self.datetime = dateutil.parser.parse(value, fuzzy=True)
                _LOG.debug(
                    'dateutil failed to parse string "%s" into a date/time,'
                    ' using fuzzy=True results in: %s', value, self.datetime, exc_info=1)
            except ValueError:
                _LOG.debug(
                    'dateutil failed to parse string "%s" into a date/time,'
                    ' even using fuzzy=True', value, exc_info=1)
        if self.datetime is not None:
            self.timezone = recode_timezone_info(self.datetime)

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
            raise NotImplementedError(f'handling of "{content_type}" not implemented')

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
        assert isinstance(folder_name, str), type(folder_name)
        if server is not self._origin_server:
            from .imap_connection import IMAPConnection
            assert isinstance(self._origin_server, IMAPConnection), type(self._origin_server)
            assert isinstance(server, IMAPConnection), type(server)
            parts = self._origin_server.retrieve_message_parts(
                self._origin_id, ['UID', 'ENVELOPE', 'FLAGS', 'INTERNALDATE', 'BODY.PEEK[]'],
                self._origin_folder)
            _LOG.warning('moving %s between servers: from %s "%s" to %s "%s"',
                         self, self._origin_server, self._origin_folder, server, folder_name)
            server.add_message(parts, folder_name)
            self._origin_server.delete_message(self._origin_id, self._origin_folder)
            return
        if folder_name == self._origin_folder:
            _LOG.debug('move_to() destination same as origin, nothing to do')
            return
        from .imap_connection import IMAPConnection
        assert isinstance(self._origin_server, IMAPConnection), type(self._origin_server)
        _LOG.warning('moving %s within same server %s: from "%s" to "%s"',
                     self, self._origin_server, self._origin_folder, folder_name)
        self._origin_server.move_message(self._origin_id, folder_name, self._origin_folder)

    def copy_to(self, server: Connection, folder: str) -> None:
        raise NotImplementedError()

    def send_via(self, server: Connection) -> None:
        server.send_message(self._email_message)

    def str_oneline(self):
        return (f'{type(self).__name__}(From:{self.from_name}<{self.from_address}>,'
                f'To:{self.to_name}<{self.to_address}>,Subject:{self.subject},'
                f'DateAndTime:{self.datetime})')

    def str_headers(self):
        return '\n'.join([
            f'From:     {self.from_address}',
            f'          {self.from_name}',
            f'Reply-To: {self.reply_to_address}',
            f'          {self.reply_to_name}',
            f'To:       {self.to_address}',
            f'          {self.to_name}',
            f'Subject:  {self.subject}',
            f'Date:     {self.date}',
            f'Time:     {self.time}',
            f'Timezone: {self.timezone}',
            f'Locally:  {self.local_date}',
            f'          {self.local_time}',
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
            f'From:     {self.from_address} {self.from_name}',
            f'Reply-To: {self.reply_to_address} {self.reply_to_name}',
            f'To:       {self.to_address} {self.to_name}',
            f'Subject:  {self.subject}',
            f'Datetime: {self.date} {self.time} {self.timezone}'
            ])

    def str_quote(self):
        raise NotImplementedError()

    def str_forward(self):
        raise NotImplementedError()

    def str_complete(self):
        return '\n'.join([
            self.str_headers(),
            '',
            f'id: {self._origin_id}',
            f'flags: {self.flags}',
            '',
            'contents{}:'.format(f' (multipart, {len(self.contents)} parts)'
                                 if len(self.contents) > 1 else ''),
            80*'=',
            (80*'=' + '\n').join(self.contents),
            80*'=',
            ])

    def __str__(self):
        return self.str_oneline()

    def __repr__(self):
        return self.str_headers_compact()
