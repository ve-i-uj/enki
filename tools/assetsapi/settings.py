import logging
from pathlib import Path
from typing import Optional

import environs

_env = environs.Env()

LOG_LEVEL: int = _env.log_level('LOG_LEVEL', logging.DEBUG)

# Будет сгенерирован (скопирован по факту) только API для модуля KBEngine, API
# сущностей и типы генерироваться не будут
ONLY_KBENGINE_API: bool = _env.bool('ONLY_KBENGINE_API', False)

# Если выставлена эта переменная, то ещё будут скопированы интерфейсы, классы
# и ряд полезных для разработки функций
ADD_ASSETSTOOLS: bool = _env.bool('ADD_ASSETSTOOLS', False)

# Директория расположения шаблонов для генерации кода
class Templates:
    _jinja_templs_dir: Path = Path(__file__).parent / 'templates'
    TYPESXML_JINJA_TEMPLATE_PATH = _jinja_templs_dir / 'typesxml.py.jinja'
    ENTITY_JINJA_TEMPLATE_PATH = _jinja_templs_dir / 'entity.py.jinja'
    USER_TYPE_PATH = _jinja_templs_dir / 'user_type.py.jinja'

GAME_ASSETS_DIR: Path = _env.path('GAME_ASSETS_DIR')
assert GAME_ASSETS_DIR != Path('.'), 'The variable "GAME_ASSETS_DIR" cannot be empty'


class AssetsDirs:
    ENTITIES_XML_PATH = GAME_ASSETS_DIR / 'scripts' / 'entities.xml'
    ENTITY_DEFS_DIR = GAME_ASSETS_DIR / 'scripts' / 'entity_defs'
    ENTITY_DEFS_COMPONENT_DIR = GAME_ASSETS_DIR / \
        'scripts' / 'entity_defs' / 'components'
    TYPES_XML_PATH = GAME_ASSETS_DIR / 'scripts' / 'entity_defs' / 'types.xml'
    USER_TYPE_DIR = GAME_ASSETS_DIR / 'scripts' / 'user_type'
    SERVER_COMMON = GAME_ASSETS_DIR / 'scripts' / 'server_common'


class CodeGenDstPath:
    ASSETSAPI_DIR: Path = AssetsDirs.SERVER_COMMON / 'assetsapi'
    ASSETSTOOLS_DIR: Path = AssetsDirs.SERVER_COMMON / 'assetstools'
    USER_TYPE_DIR: Path = ASSETSAPI_DIR / 'user_type'
    USER_TYPE_INIT: Path = USER_TYPE_DIR / '__init__.py'
    TYPESXML: Path = ASSETSAPI_DIR / 'typesxml.py'
    TYPESXML_WITHOUT_CONVERTERS: Path = USER_TYPE_DIR / '_typesxml_without_converters.py'
    ENTITIES: Path = ASSETSAPI_DIR / 'entity'

SITE_PACKAGE_DIR: Optional[Path] = _env.path('SITE_PACKAGE_DIR', None)


class EnkiPaths:
    ENKI_ROOT: Path = Path(__file__).parent.parent.parent
    FORCOPY_DIR = ENKI_ROOT / 'tools' / 'assetsapi' / 'forcopy'
    ASSETSAPI_FOR_COPY_DIR = FORCOPY_DIR / 'assetsapi'
    ASSETSTOOLS_FOR_COPY_DIR = FORCOPY_DIR / 'assetstools'
