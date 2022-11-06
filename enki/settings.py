"""Settings.

Settings are loaded from the .env file located in the root directory.
"""

import datetime
import enum
import logging
import os
import pathlib
from dataclasses import dataclass

import environs

logger = logging.getLogger(__name__)

_env = environs.Env()

SECOND = int(datetime.timedelta(seconds=1).total_seconds())


def init(proj_root_path: str):
    print('proj_root_path = ', proj_root_path)
    _env.read_env(os.path.join(proj_root_path, '.env'), recurse=False)


# TODO: [02.07.2021 burov_alexey@mail.ru]:
# Нигде не используется
class ComponentEnum(enum.Enum):
    """Id of the KBEngine component."""
    LOGINAPP = 2
    BASEAPP = 6

WAITING_FOR_SERVER_TIMEOUT = 2 * SECOND
CONNECT_TO_SERVER_TIMEOUT = 5 * SECOND
SERVER_TICK_PERIOD = 30 * SECOND

TCP_CHUNK_SIZE: int = 65535

NO_ENTITY_CLS_ID = 0
NO_ENTITY_ID = 0
NO_ID = 0
