"""Настройки сервиса."""

import logging
import os

import environs

logger = logging.getLogger(__name__)

ENV = environs.Env()


def init(proj_root_path: str):
    print('proj_root_path = ', proj_root_path)
    ENV.read_env(os.path.join(proj_root_path, '.env'), recurse=False)

