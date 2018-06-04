"""JSON configuration reader."""

import json
import pathlib

# from ingit.json_config import file_to_json

DEFAULT_CONFIG_PATH = pathlib.Path('maildaemon_config.json')


def str_to_json(text: str) -> dict:
    """Convert JSON string into an object."""
    try:
        return json.loads(text)
    except json.decoder.JSONDecodeError as err:
        lines = text.splitlines(keepends=True)
        raise ValueError('\n{}{}\n{}'.format(
            ''.join(lines[max(0, err.lineno - 10):err.lineno]), '-' * err.colno,
            ''.join(lines[err.lineno:min(err.lineno + 10, len(lines))]))) from err


def file_to_json(path: pathlib.Path) -> dict:
    """Create JSON object from a file."""
    with open(str(path), 'r', encoding='utf-8') as json_file:
        text = json_file.read()
    try:
        data = str_to_json(text)
    except ValueError as err:
        raise ValueError('in file "{}"'.format(path)) from err
    return data


def load_config(path: pathlib.Path = DEFAULT_CONFIG_PATH):
    """Load maildaemon configuration from file."""
    config = file_to_json(path)
    try:
        validate_config(config)
    except AssertionError as err:
        raise ValueError('{} is an invalid maildaemon config'.format(path)) from err
    return config


def validate_config(config: dict):
    """Validate the maildaemon configuration."""
    for name, connection in config.get('connections', {}).items():
        assert isinstance(name, str), type(name)
        assert name, name
        assert 'protocol' in connection, connection
        assert isinstance(connection['protocol'], str), type(connection['protocol'])
        assert connection['protocol'], connection
        assert 'domain' in connection, connection
        assert isinstance(connection['domain'], str), type(connection['domain'])
        assert connection['domain'], connection
        assert isinstance(connection.get('ssl', False), int), type(connection['port'])
        assert isinstance(connection.get('port', 1), int), type(connection['port'])
        assert connection.get('port', 1) > 0, connection['port']
        assert isinstance(connection.get('login', 'test'), str), type(connection['login'])
        assert connection.get('login', 'test'), connection['login']
        assert isinstance(connection.get('password', 'test'), str), type(connection['password'])
        assert connection.get('password', 'test'), connection['password']
    for name, filter_ in config.get('filters', {}).items():
        for connection_name in filter_.get('connections', []):
            assert connection_name in config['connections']
        assert 'condition' in filter_, filter_
        assert isinstance(filter_['condition'], str), type(filter_['condition'])
        for action in filter_.get('actions', []):
            assert isinstance(action, str), type(action)
