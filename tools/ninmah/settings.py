import logging
import pathlib

import environs

from enki.enkitype import AppAddr


_env = environs.Env()

_LOGIN_APP_HOST: str = _env.str('LOGIN_APP_HOST')
_LOGIN_APP_PORT = _env.int('LOGIN_APP_PORT')
LOGIN_APP_ADDR = AppAddr(_LOGIN_APP_HOST, _LOGIN_APP_PORT)

GAME_ASSETS_DIR: pathlib.Path = _env.path('GAME_ASSETS_DIR')
KBENGINE_XML_PATH = GAME_ASSETS_DIR / 'res' / 'server' / 'kbengine.xml'
ENTITIES_XML_PATH = GAME_ASSETS_DIR / 'scripts' / 'entities.xml'
ENTITY_DEFS_DIR = GAME_ASSETS_DIR / 'scripts' / 'entity_defs'
ENTITY_DEFS_COMPONENT_DIR = GAME_ASSETS_DIR / \
    'scripts' / 'entity_defs' / 'components'

ACCOUNT_NAME: str = _env.str('ACCOUNT_NAME')
PASSWORD: str = _env.str('PASSWORD')

GAME_GENERATED_CLIENT_API_DIR: pathlib.Path = _env.path(
    'GAME_GENERATED_CLIENT_API_DIR')

GAME_ACCOUNT_NAME: str = _env.str('GAME_ACCOUNT_NAME')
GAME_PASSWORD: str = _env.str('GAME_PASSWORD')


class CodeGenDstPath:
    ROOT = GAME_GENERATED_CLIENT_API_DIR
    APP = ROOT / 'app'
    SERIALIZER_ENTITY = ROOT / 'eserializer' / '_generated'
    ENTITY = ROOT / 'gameentity' / '_generated'
    TYPE = ROOT / 'deftype/_generated.py'
    # SERVERERROR = ROOT / 'servererror/_generated.py'
    KBENGINE_XML = ROOT / 'kbenginexml.py'


# Include description of the kbengine messages in the generated code
INCLUDE_MSGES: bool = _env.bool('INCLUDE_MSGES', False)

LOG_LEVEL: int = _env.log_level('LOG_LEVEL', logging.DEBUG)

PROJECT_SITE: str = 'https://github.com/ve-i-uj/enki'
