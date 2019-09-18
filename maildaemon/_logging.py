
import logging
import logging.config


def configure_logging():
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'brief': {
                '()': 'colorlog.ColoredFormatter',
                'style': '{',
                'format': '{name} [{log_color}{levelname}{reset}] {message}'},
            'precise': {'style': '{', 'format': '{asctime} {name} [{levelname}] {message}'}
            },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler', 'formatter': 'brief', 'level': logging.NOTSET,
                'stream': 'ext://sys.stdout'}
            },
        'root': {'level': logging.WARNING, 'handlers': ['console']}
        })
