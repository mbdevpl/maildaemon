"""


defaults ports info: https://www.siteground.com/tutorials/email/pop3-imap-smtp-ports.htm
"""

import abc
import getpass
import typing as t

class Connection(metaclass=abc.ABCMeta):
    """
    General notion of a connection to some server.
    """

    ports = []
    ssl_ports = []

    @classmethod
    def from_dict(cls, data: dict) -> 'Connection':

        try:
            connection = cls(domain=data['domain'], ssl=data['ssl'], port=data['port'])
        except KeyError:
            try:
                connection = cls(domain=data['domain'], ssl=data['ssl'])
            except KeyError:
                try:
                    connection = cls(domain=data['domain'])
                except KeyError:
                    raise RuntimeError(
                        'failed to construct {} from dictionary {}'.format(cls.__name__, data))

        try:
            connection.login = data['login']
        except KeyError:
            pass
        try:
            connection.password = data['password']
        except KeyError:
            pass

        return connection

    def __init__(self, domain: str, ssl: bool=True, port: t.Optional[int]=None):

        self.domain = domain # type: str
        self.ssl = ssl # type: bool
        self._port = port # type: t.Optional[int]

        self._login = None # type: t.Optional[str]
        self._password = None # type: t.Optional[str]
        #self._link = None # type: t.Any

    @property
    def port(self) -> int:

        if self._port is not None:
            assert isinstance(self._port, int)
            #assert self._port in type(self).ssl_ports if self.ssl else self._port in type(self).ports
            return self._port

        if self.ssl:
            return type(self).ssl_ports[0]
        else:
            return type(self).ports[0]

    @port.setter
    def port(self, port: t.Optional[int]):

        assert port is None or isinstance(port, int)
        #if __debug__:
        #    if isinstance(port, int):
        #        assert port in type(self).ssl_ports if self.ssl else port in type(self).ports

        self._port = port

    @property
    def login(self) -> str:

        assert self._login is None or isinstance(self._login, str)

        return getpass.getuser() if self._login is None else self._login

    @login.setter
    def login(self, login: t.Optional[str]):

        assert login is None or isinstance(login, str)

        self._login = login

    @property
    def password(self) -> str:

        assert self._password is None or isinstance(self._password, str)

        return getpass.getpass() if self._password is None else self._password

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

        args = [self.domain, str(self.port), 'SSL' if self.ssl else 'plaintext']
        return '{}({})'.format(type(self).__name__, ', '.join(args))
