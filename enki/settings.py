"""Settings.

Settings are loaded from the .env file located in the root directory.
"""

import logging
import os
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
