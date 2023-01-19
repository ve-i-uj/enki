"""Logging settings."""

import logging
import sys

DEBUG_FORMAT = '[%(levelname)-7s] [%(asctime)s] [%(threadName)s] [%(filename)s:%(lineno)s - %(funcName)s()] %(message)s'
INFO_FORMAT = '[%(levelname)-7s] [%(asctime)s] %(message)s'


def setup_root_logger(level_name: str):
    level = logging.getLevelName(level_name)
    if not isinstance(level, int):
        logging.error(f'There is no debug level "{level_name}". Exit')
        sys.exit(1)
    logger = logging.getLogger()
    logger.setLevel(level)
    stream_handler = logging.StreamHandler(sys.stdout)

    if level > logging.DEBUG:
        format_ = INFO_FORMAT
    else:
        format_ = DEBUG_FORMAT
    formatter = logging.Formatter(format_)
    stream_handler.setFormatter(formatter)
    logger.handlers = [stream_handler]
