"""Settings.

Settings are loaded from the .env file located in the root directory.
"""

import enum
import logging
import os
import pathlib
from dataclasses import dataclass

import environs

logger = logging.getLogger(__name__)

_env = environs.Env()


def init(proj_root_path: str):
    print('proj_root_path = ', proj_root_path)
    _env.read_env(os.path.join(proj_root_path, '.env'), recurse=False)


@dataclass
class AppAddr:
    """Address of a KBE component."""
    host: str
    port: int


LOGIN_APP_ADDR = AppAddr('localhost', 20013)


# TODO: [02.07.2021 burov_alexey@mail.ru]:
# Нигде не используется
class ComponentEnum(enum.Enum):
    """Id of the KBEngine component."""
    LOGINAPP = 2
    BASEAPP = 6


ACCOUNT_NAME = '1'
PASSWORD = '1'


# TODO: [02.01.2021 1:38 burov_alexey@mail.ru]
# Take path from command line arguments
class CodeGenDstPath:
    _proj_dir = pathlib.Path(__file__).resolve().parent
    APP = _proj_dir / 'descr/app/'
    ENTITY = _proj_dir / 'descr/entity/_generated/'
    TYPE = _proj_dir / 'descr/_deftype/_generated.py'
    SERVERERROR = _proj_dir / 'descr/servererror/_generated.py'


WAITING_FOR_SERVER_TIMEOUT = 2
