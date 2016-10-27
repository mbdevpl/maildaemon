
import configparser

DEFAULT_CONFIG_PATH = '.maildaemon.config'

def load_config(path: str=DEFAULT_CONFIG_PATH):

    config = configparser.ConfigParser()

    config.read(path)

    connections = {}

    for section, contents in config.items():
        if section.startswith('connection:'):
            connection = {}
            try:
                connection['protocol'] = contents['protocol']
            except KeyError as err:
                raise RuntimeError('protocol must be provided in connection configuration') from err
            try:
                connection['domain'] = contents['domain']
            except KeyError as err:
                raise RuntimeError('domain must be provided in connection configuration') from err
            try:
                connection['ssl'] = bool(contents['ssl'])
            except KeyError:
                pass
            try:
                connection['port'] = int(contents['port'])
            except KeyError:
                pass
            try:
                connection['login'] = contents['login']
            except KeyError:
                pass
            try:
                connection['password'] = contents['password']
            except KeyError:
                pass
            connections[section.replace('connection:', '', 1).strip()] = connection

    return  {
        'connections': connections
        }
