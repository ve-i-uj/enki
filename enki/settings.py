"""Settings.

Settings are loaded from the .env file located in the root directory.

* No dependences *
"""

import datetime
import logging
import os

import environs

logger = logging.getLogger(__name__)

_env = environs.Env()

MINUTE = int(datetime.timedelta(minutes=1).total_seconds())
SECOND = int(datetime.timedelta(seconds=1).total_seconds())
MSECOND: float = SECOND / 1000


def init(proj_root_path: str):
    print('proj_root_path = ', proj_root_path)
    _env.read_env(os.path.join(proj_root_path, '.env'), recurse=False)


WAITING_FOR_SERVER_TIMEOUT = 2 * SECOND
CONNECT_TO_SERVER_TIMEOUT = 5 * SECOND
SERVER_TICK_PERIOD = 30 * SECOND

TCP_CHUNK_SIZE: int = 65535

NO_ENTITY_CLS_ID = 0
NO_ENTITY_ID = 0
NO_ID = 0

NO_COMPONENT_PROPERTY_ID = 0
NO_COMPONENT_NAME = ''

NO_POS_DIR_VALUE = -1589.123409871

LOG_LEVEL: int = _env.log_level('LOG_LEVEL', logging.DEBUG)

# Нужно так же учитывать примерный интревала удержания GIL (~5ms). Быстрее работать не будет.
# https://pythonspeed.com/articles/python-gil/
GAME_TICK = 20 * MSECOND
GAME_HALF_TICK = GAME_TICK / 2
