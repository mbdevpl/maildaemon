"""Generic interface for managing a connection with a server.

defaults ports info: https://www.siteground.com/tutorials/email/pop3-imap-smtp-ports.htm
"""

import abc
import getpass
import typing as t


class Response:
    """Helper class for automatic decoding and printing server responses."""

    def __init__(self, response: t.Union[str, bytes, t.List[t.Union[str, bytes]]]):
        self.response = response

    def __str__(self):
        if isinstance(self.response, str):
            return self.response
        if isinstance(self.response, bytes):
            return self.response.decode()
        return str([r.decode() if isinstance(r, bytes) else r for r in self.response])


class Connection(metaclass=abc.ABCMeta):
    """General notion of a connection to some server."""

    ports = []
    ssl_ports = []

    @classmethod
    def from_dict(cls, data: dict) -> 'Connection':
        kwargs = {key: data[key] for key in ('domain', 'port', 'ssl', 'oauth') if key in data}
        connection = cls(**kwargs)
        if connection.oauth:
            connection.oauth_data = data['oauth-data']

        try:
            connection.login = data['login']
        except KeyError:
            pass
        try:
            connection.password = data['password']
        except KeyError:
            pass

        return connection

    def __init__(self, domain: str, port: t.Optional[int] = None, ssl: bool = True,
                 oauth: bool = False):
        assert isinstance(domain, str), type(domain)
        assert isinstance(port, int), type(port)
        assert isinstance(ssl, bool), type(ssl)
        assert isinstance(oauth, bool), type(oauth)
        self.domain = domain  # type: str
        self._port = port  # type: t.Optional[int]
        self.ssl = ssl  # type: bool
        self.oauth = oauth  # type: bool
        self.oauth_data = None  # type: dict

        self._login = None  # type: t.Optional[str]
        self._password = None  # type: t.Optional[str]
        # self._link = None  # type: t.Any

    @property
    def port(self) -> int:
        if self._port is not None:
            assert isinstance(self._port, int)
            # assert self._port in type(self).ssl_ports if self.ssl \
            #    else self._port in type(self).ports
            return self._port

        if self.ssl:
            return type(self).ssl_ports[0]
        return type(self).ports[0]

    @port.setter
    def port(self, port: t.Optional[int]):
        assert port is None or isinstance(port, int)
        # if __debug__:
        #    if isinstance(port, int):
        #        assert port in type(self).ssl_ports if self.ssl else port in type(self).ports
        self._port = port

    @property
    def login(self) -> str:
        assert self._login is None or isinstance(self._login, str)
        if self._login is None:
            print(f'User at {self.domain}:{self.port}: ', end='', flush=True)
            self._login = getpass.getuser()
        return self._login

    @login.setter
    def login(self, login: t.Optional[str]):
        assert login is None or isinstance(login, str)
        self._login = login

    @property
    def password(self) -> str:
        assert self._password is None or isinstance(self._password, str)
        if self._password is None:
            user = 'unknown user' if self._login is None else f'user {self.login}'
            self._password = getpass.getpass(f'Password for {user} at {self.domain}:{self.port}: ')
        return self._password

    @password.setter
    def password(self, password: t.Optional[str]):
        assert password is None or isinstance(password, str)
        self._password = password

    @abc.abstractmethod
    def connect(self) -> None:
        pass

    @abc.abstractmethod
    def is_alive(self) -> bool:
        pass

    @abc.abstractmethod
    def disconnect(self) -> None:
        pass

    def __repr__(self):
        return f'{type(self).__name__}({self.domain}:{self.port}{"+SSL" if self.ssl else ""}' \
            f'{"+OAUTH" if self.oauth else ""})'
