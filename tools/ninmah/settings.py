import logging
import pathlib

import environs

from enki.enkitype import AppAddr


_env = environs.Env()

_LOGIN_APP_HOST: str = _env.str('LOGIN_APP_HOST')
_LOGIN_APP_PORT = _env.int('LOGIN_APP_PORT')
LOGIN_APP_ADDR = AppAddr(_LOGIN_APP_HOST, _LOGIN_APP_PORT)

ASSETS_PATH: pathlib.Path = _env.path('ASSETS_PATH')
KBENGINE_XML_PATH = ASSETS_PATH / 'res' / 'server' / 'kbengine.xml'
ENTITIES_XML_PATH = ASSETS_PATH / 'scripts' / 'entities.xml'
ENTITY_DEFS_DIR = ASSETS_PATH / 'scripts' / 'entity_defs'
ENTITY_DEFS_COMPONENT_DIR = ASSETS_PATH / 'scripts' / 'entity_defs' / 'components'

ACCOUNT_NAME: str = _env.str('ACCOUNT_NAME')
PASSWORD: str = _env.str('PASSWORD')

DST_DIR: pathlib.Path = _env.path('DST_DIR')
class CodeGenDstPath:
    ROOT = DST_DIR
    APP = ROOT / 'app'
    ENTITY = ROOT / 'entity/_generated'
    TYPE = ROOT / 'deftype/_generated.py'
    # SERVERERROR = ROOT / 'servererror/_generated.py'
    KBENGINE_XML = ROOT / 'kbenginexml.py'

# Include description of the kbengine messages in the generated code
INCLUDE_MSGES: bool = _env.bool('INCLUDE_MSGES', False)

LOG_LEVEL: int = _env.log_level('LOG_LEVEL', logging.DEBUG)

PROJECT_SITE: str ='https://github.com/ve-i-uj/enki'
