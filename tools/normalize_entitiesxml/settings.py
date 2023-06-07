import logging
from pathlib import Path

import environs

_env = environs.Env()

LOG_LEVEL: int = _env.log_level('LOG_LEVEL', logging.DEBUG)

GAME_ASSETS_DIR: Path = _env.path('GAME_ASSETS_DIR')
assert GAME_ASSETS_DIR != Path('.'), 'The variable "GAME_ASSETS_DIR" cannot be empty'
ENTITIES_XML_PATH = GAME_ASSETS_DIR / 'scripts' / 'entities.xml'
ENTITY_DEFS_DIR = GAME_ASSETS_DIR / 'scripts' / 'entity_defs'

UPDATED_ENTITIES_XML_PATH: Path = _env.path(
    'UPDATED_ENTITIES_XML_PATH')
assert UPDATED_ENTITIES_XML_PATH != Path('.'), \
    'The variable "UPDATED_ENTITIES_XML_PATH" cannot be empty'

ADD_EMPTY_ENTITY_MODULE: bool = _env.bool('ADD_EMPTY_ENTITY_MODULE', False)
