"""Настройки компонента Supervisor."""

import logging

import environs

_env = environs.Env()

LOG_LEVEL: int = _env.log_level("LOG_LEVEL", logging.DEBUG)

KBE_MACHINE_TCP_PORT: int = _env.int("KBE_MACHINE_TCP_PORT")
KBE_MACHINE_HOST: str = _env.str("KBE_MACHINE_HOST")
