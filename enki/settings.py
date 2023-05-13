"""Settings."""

import datetime
import logging

import environs

logger = logging.getLogger(__name__)

_env = environs.Env()

MINUTE = int(datetime.timedelta(minutes=1).total_seconds())
SECOND = int(datetime.timedelta(seconds=1).total_seconds())
MSECOND: float = SECOND / 1000

WAITING_FOR_SERVER_TIMEOUT = 2 * SECOND
CONNECT_TO_SERVER_TIMEOUT = 5 * SECOND
SERVER_TICK_PERIOD = 30 * SECOND

TCP_CHUNK_SIZE: int = 65535

LOG_LEVEL: int = _env.log_level('LOG_LEVEL', logging.DEBUG)

# Нужно так же учитывать примерный интревала удержания GIL (~5ms). Быстрее работать не будет.
# https://pythonspeed.com/articles/python-gil/
GAME_TICK = 20 * MSECOND
GAME_HALF_TICK = GAME_TICK / 2
