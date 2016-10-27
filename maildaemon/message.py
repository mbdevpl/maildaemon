
import datetime
import email.header
import email.message
import logging

import dateutil.parser
#import pytz

#from .server import Server
#from .smtp_server import SMTPServer

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
    else:
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

def recode_contents(raw_part) -> str:
    if not raw_part.get_content_charset():
        raise ValueError('no content charset')
    return raw_part.get_payload(decode=True).decode(raw_part.get_content_charset())

def print_message(msg: email.message.EmailMessage) -> None:
    raise RuntimeError('deprecated')
    #msg.get_charset()
    #msg.get_content_charset()
    #msg.as_string()
    #msg.items()
    parts = []
    if msg.is_multipart():
        parts = msg.get_payload()
        print('multipart, {} parts'.format(len(parts)))
        #print(msg.get_charsets())
    else:
        parts = [msg]
    print('From:    """{}"""'.format(recode_header(msg['From'])))
    print('To:      """{}"""'.format(recode_header(msg['To'])))
    print('Subject: """{}"""'.format(recode_header(msg['Subject'])))
    #print('msg['Reply-To']
    print(msg.keys())
    for part in parts:
        print(part.keys())
        #print(part.get_charset())
        print(80*'=')
        print(recode_contents(part))
    return

class Message:

    @classmethod
    def from_email_message(cls, msg: email.message.EmailMessage, server=None, folder=None, msg_id=None):

        m = cls()
        m._email_message = msg
        m._origin_server = server
        m._origin_folder = folder
        m._origin_id = msg_id

        for key, value in msg.items():
            if key == 'From':
                m.from_address, m.from_name = split_name_and_address(str(recode_header(value)))
            elif key == 'Reply-To':
                m.reply_to_address, m.reply_to_name = split_name_and_address(str(recode_header(value)))
            elif key == 'To':
                m.to_address, m.to_name = split_name_and_address(str(recode_header(value)))
            elif key == 'Subject':
                m.subject = recode_header(value)
            elif key == 'Date':
                _datetime = dateutil.parser.parse(value) # type: datetime.datetime
                m.datetime = _datetime
                m.date = _datetime.date()
                m.time = _datetime.time()
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
            text = recode_contents(part)
            #if text.startswith('<'):
            #    continue
            m.contents.append(text)
        return m

    def __init__(self):

        self._email_message = None # type: email.message.EmailMessage
        self._origin_server = None # type: Server
        self._origin_folder = None # type: str
        self._origin_id = None # type: int

        self.from_address = None
        self.from_name = None
        self.reply_to_address = None
        self.reply_to_name = None
        self.to_address = None
        self.to_name = None
        self.subject = None
        self.date = None
        self.time = None
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

    def move_to(self, server: 'Server', folder: str) -> None:

        if server is self._origin_server:
            if folder == self._origin_folder:
                _LOG.debug('move_to() destination same as origin, nothing to do')
            _LOG.error('move_to() not implemented moving within same server')
            #raise NotImplementedError()

        else:
            _LOG.error('move_to() not implemented moving between servers')
            #raise NotImplementedError()

    def copy_to(self, server: 'Server', folder: str) -> None:

        raise NotImplementedError()

    def send_via(self, server: 'Server') -> None:

        server.send_message(self)

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
            #'',
            #'  Received: {}'.format(self.received),
            #'  Return-Path: {}'.format(self.return_path),
            #'  Envelope-To: {}'.format(self.envelope_to),
            #'  Message-Id: {}'.format(self.message_id),
            #'  Content-Type: {}'.format(self.content_type),
            #'Other headers:',
            #'\n'.join(['  {}: {}'.format(k, v) for k, v in self.other_headers]),
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
            'Contents{}:'.format(' (multipart, {} parts)'.format(len(self.contents)) if len(self.contents) > 1 else ''),
            80*'=',
            (80*'=' + '\n').join(self.contents),
            80*'=',
            ])

    def __str__(self):
        return self.str_complete()

    def __repr__(self):
        return self.str_headers_compact()


