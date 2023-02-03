"""Settings.

Settings are loaded from the .env file located in the root directory.
"""

import logging
import os
from enki.enkitype import AppAddr

import environs

_env = environs.Env()

logger = logging.getLogger(__name__)


def init(proj_root_path: str):
    print('proj_root_path = ', proj_root_path)
    _env.read_env(os.path.join(proj_root_path, '.env'), recurse=False)


LOG_LEVEL: int = _env.log_level('LOG_LEVEL', logging.DEBUG)

SHEDU_SUPERVISOR_ADDR = AppAddr(
    _env.str('SHEDU_SUPERVISOR_HOST'),
    _env.str('SHEDU_SUPERVISOR_HOST')
)
