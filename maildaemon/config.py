
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
            connection_name = section.replace('connection:', '', 1).strip()
            connection = {}
            try:
                connection['protocol'] = contents['protocol']
            except KeyError as err:
                raise RuntimeError(
                    'no protocol provided in configuration for connection "{}"'
                    .format(connection_name)) from err
            try:
                connection['domain'] = contents['domain']
            except KeyError as err:
                raise RuntimeError(
                    'no domain provided in configuration for connection "{}"'
                    .format(connection_name)) from err
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
            connections[connection_name] = connection

        if section.startswith('filter:'):
            filter_name = section.replace('filter:', '', 1).strip()
            filter_ = {}
            try:
                filter_['connections'] = [c.strip() for c in contents['connections'].split(',')]
            except KeyError:
                pass
            try:
                filter_['condition'] = [
                    [c.strip() for c in d.strip().split(' and ')]
                    for d in contents['condition'].split(' or ')]
            except KeyError:
                pass
            try:
                filter_['actions'] = [a.strip() for a in contents['actions'].split(',')]
            except KeyError as err:
                raise RuntimeError(
                    'no action provided in configuration for filter "{}"'
                    .format(filter_name)) from err
            filters[filter_name] = filter_

    return  {
        'connections': connections,
        'filters': filters
        }
