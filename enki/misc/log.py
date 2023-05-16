"""Logging settings."""

import logging
import sys
from typing import Optional

DEBUG_FORMAT = '[%(levelname)-7s] [%(asctime)s] [%(threadName)s] [%(filename)s:%(lineno)s - %(funcName)s()] %(message)s'
INFO_FORMAT = '[%(levelname)-7s] [%(asctime)s] %(message)s'


def setup_root_logger(level_name: str, log_format: Optional[str] = None):
    level = logging.getLevelName(level_name)
    if not isinstance(level, int):
        logging.error(f'There is no debug level "{level_name}". Exit')
        sys.exit(1)
    logger = logging.getLogger()
    logger.setLevel(level)
    stream_handler = logging.StreamHandler(sys.stdout)

    if log_format is None:
        log_format = DEBUG_FORMAT
        if level > logging.DEBUG:
            log_format = INFO_FORMAT
    formatter = logging.Formatter(log_format)
    stream_handler.setFormatter(formatter)
    logger.handlers = [stream_handler]
