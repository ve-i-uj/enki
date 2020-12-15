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


LOGIN = '1'
PASSWORD = '1'


class CodeGenDst:
    CLIENT = pathlib.Path('/home/leto/code/pCloud/2PeopleCompany/enki/enki/message/spec/app/client.py')
    BASEAPP = pathlib.Path('/home/leto/code/pCloud/2PeopleCompany/enki/enki/message/spec/app/baseapp.py')
    LOGINAPP = pathlib.Path('/home/leto/code/pCloud/2PeopleCompany/enki/enki/message/spec/app/loginapp.py')
