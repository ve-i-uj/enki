import logging
import pathlib

import environs

_env = environs.Env()

LOG_LEVEL: int = _env.log_level('LOG_LEVEL', logging.DEBUG)

GAME_ASSETS_DIR: pathlib.Path = _env.path('GAME_ASSETS_DIR')
assert GAME_ASSETS_DIR != pathlib.Path('.'), 'The variable "GAME_ASSETS_DIR" cannot be empty'
ENTITIES_XML_PATH = GAME_ASSETS_DIR / 'scripts' / 'entities.xml'
ENTITY_DEFS_DIR = GAME_ASSETS_DIR / 'scripts' / 'entity_defs'

UPDATED_ENTITIES_XML_PATH: pathlib.Path = _env.path(
    'UPDATED_ENTITIES_XML_PATH')
assert UPDATED_ENTITIES_XML_PATH != pathlib.Path('.'), \
    'The variable "UPDATED_ENTITIES_XML_PATH" cannot be empty'
