
import ast
import configparser

DEFAULT_CONFIG_PATH = '.maildaemon.config'

def load_config(path: str=DEFAULT_CONFIG_PATH):

    config = configparser.ConfigParser()

    config.read(path)

    connections = {}
    filters = {}

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
                connection['ssl'] = ast.literal_eval(contents['ssl'])
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

        if section.startswith('filter:'):
            filter_ = {}
            try:
                filter_['connections'] = [c.strip() for c in contents['connections'].split(',')]
            except KeyError:
                pass
            try:
                filter_['condition'] = [[c.strip() for c in d.strip().split(' and ')] for d in contents['condition'].split(' or ')]
            except KeyError:
                pass
            try:
                filter_['actions'] = [a.strip() for a in contents['actions'].split(',')]
            except KeyError:
                pass
            filters[section.replace('filter:', '', 1).strip()] = filter_

    return  {
        'connections': connections,
        'filters': filters
        }
