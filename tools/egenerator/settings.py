import logging
from pathlib import Path

import environs
from marshmallow.validate import OneOf, Length, Email

from enki.core.enkitype import AppAddr


_env = environs.Env()

_LOGINAPP_HOST: str = _env.str('LOGINAPP_HOST', validate=[Length(min=1)])
_LOGINAPP_PORT = _env.int('LOGINAPP_PORT')
LOGINAPP_ADDR = AppAddr(_LOGINAPP_HOST, _LOGINAPP_PORT)

GAME_ASSETS_DIR: Path = _env.path('GAME_ASSETS_DIR')
assert GAME_ASSETS_DIR != Path('.'), 'The variable "GAME_ASSETS_DIR" cannot be empty'
KBENGINE_XML_PATH = GAME_ASSETS_DIR / 'res' / 'server' / 'kbengine.xml'
ENTITIES_XML_PATH = GAME_ASSETS_DIR / 'scripts' / 'entities.xml'
ENTITY_DEFS_DIR = GAME_ASSETS_DIR / 'scripts' / 'entity_defs'
ENTITY_DEFS_COMPONENT_DIR = GAME_ASSETS_DIR / \
    'scripts' / 'entity_defs' / 'components'

GAME_ACCOUNT_NAME: str = _env.str('GAME_ACCOUNT_NAME', validate=[Length(min=1)])
GAME_PASSWORD: str = _env.str('GAME_PASSWORD', validate=[Length(min=1)])

GAME_GENERATED_CLIENT_API_DIR: Path = _env.path(
    'GAME_GENERATED_CLIENT_API_DIR')
assert GAME_GENERATED_CLIENT_API_DIR != Path('.'), \
    'The variable "GAME_GENERATED_CLIENT_API_DIR" cannot be empty'


class CodeGenDstPath:
    ROOT: Path = GAME_GENERATED_CLIENT_API_DIR
    APP: Path = ROOT / 'app'
    SERIALIZER_ENTITY: Path = ROOT / 'eserializer' / '_generated'
    ENTITY: Path = ROOT / 'gameentity' / '_generated'
    TYPE: Path = ROOT / 'deftype/_generated.py'
    SERVERERROR: Path = ROOT / 'servererror/_generated.py'
    KBENGINE_XML: Path = ROOT / 'kbenginexml.py'


# Include description of the kbengine messages in the generated code
INCLUDE_MSGES: bool = _env.bool('INCLUDE_MSGES', False)
# Коды ошибок от сервера. В enki используется захардкоженный enum, динамическое
# обновление ошибок не используется.
INCLUDE_ERRORS: bool = _env.bool('INCLUDE_MSGES', False)

LOG_LEVEL: int = _env.log_level('LOG_LEVEL', logging.DEBUG)

PROJECT_SITE: str = 'https://github.com/ve-i-uj/enki'

# Директория расположения шаблонов для генерации кода
JINJA_TEMPLS_DIR: Path = Path(__file__).parent / 'templates'
