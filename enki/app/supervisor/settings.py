"""Настройки компонента Supervisor."""

import environs

from enki.settings import *

_env = environs.Env()

KBE_MACHINE_TCP_PORT: int = _env.int('KBE_MACHINE_TCP_PORT')
KBE_MACHINE_HOST: str = _env.str('KBE_MACHINE_HOST')
