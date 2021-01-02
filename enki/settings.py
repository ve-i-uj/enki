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


class ComponentEnum(enum.Enum):
    LOGINAPP = 2
    BASEAPP = 6


ACCOUNT_NAME = '1'
PASSWORD = '1'


# TODO: [02.01.2021 1:38 burov_alexey@mail.ru]
# Take path from command line arguments
class CodeGenDstPath:
    APP = pathlib.Path('/home/leto/code/pCloud/2PeopleCompany/enki/enki/spec/message/app/')
    ENTITY = pathlib.Path('/home/leto/code/pCloud/2PeopleCompany/enki/enki/spec/entity/')
    SERVERERROR = pathlib.Path('/home/leto/code/pCloud/2PeopleCompany/enki/enki/spec/servererror.py')


WAITING_FOR_SERVER_TIMEOUT = 2
