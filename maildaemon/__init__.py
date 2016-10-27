"""
This is "__init__.py" file of maildaemon module.
"""

import logging
import logging.config

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'brief': {'style': '{', 'format': '{name} [{levelname}] {message}'},
        'precise': {'style': '{', 'format': '{asctime} {name} [{levelname}] {message}'}
        },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler', 'formatter': 'brief', 'level': logging.NOTSET,
            'stream': 'ext://sys.stdout'}
        },
    'root': {'level': logging.DEBUG, 'handlers': ['console']}
    })
