"""Logging settings."""

from __future__ import annotations

import logging
import sys

_DEBUG_FORMAT = "[%(levelname)-7s] [%(asctime)s] [%(threadName)s] [%(filename)s:%(lineno)s - %(funcName)s()] %(message)s"  # noqa: E501 # pylint: disable=line-too-long
_INFO_FORMAT = "[%(levelname)-7s] [%(asctime)s] %(message)s"

logger = logging.getLogger(__name__)


def setup_root_logger(level_name: str, log_format: str | None = None) -> None:
    """Установить настройки корневого логера.

    Args:
        level_name (str): уровень логирования
        log_format (str | None, optional): формат логирования, если задан

    """
    level = logging.getLevelName(level_name)
    if not isinstance(level, int):
        logger.error('There is no logging level "{%s}". Exit', level_name)
        sys.exit(1)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    stream_handler = logging.StreamHandler(sys.stdout)

    # Если формат логов не задан, то формат будет выбран на основе уровня
    # логирования.
    if log_format is None:
        log_format = _DEBUG_FORMAT
        if level > logging.DEBUG:
            log_format = _INFO_FORMAT
    formatter = logging.Formatter(log_format)
    stream_handler.setFormatter(formatter)

    root_logger.handlers = [stream_handler]

    root_logger.info("Logger set")
