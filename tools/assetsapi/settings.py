import logging
from pathlib import Path
from typing import Optional

import environs

_env = environs.Env()

LOG_LEVEL: int = _env.log_level('LOG_LEVEL', logging.DEBUG)

# Директория расположения шаблонов для генерации кода
class Templates:
    _jinja_templs_dir: Path = Path(__file__).parent / 'templates'
    TYPESXML_JINJA_TEMPLATE_PATH = _jinja_templs_dir / 'typesxml.py.jinja'
    ENTITY_JINJA_TEMPLATE_PATH = _jinja_templs_dir / 'entity.py.jinja'

GAME_ASSETS_DIR: Path = _env.path('GAME_ASSETS_DIR')
assert GAME_ASSETS_DIR != Path('.'), 'The variable "GAME_ASSETS_DIR" cannot be empty'


class AssetsDirs:
    ENTITIES_XML_PATH = GAME_ASSETS_DIR / 'scripts' / 'entities.xml'
    ENTITY_DEFS_DIR = GAME_ASSETS_DIR / 'scripts' / 'entity_defs'
    ENTITY_DEFS_COMPONENT_DIR = GAME_ASSETS_DIR / \
        'scripts' / 'entity_defs' / 'components'
    TYPES_XML_PATH = GAME_ASSETS_DIR / 'scripts' / 'entity_defs' / 'types.xml'
    USER_TYPE_DIR = GAME_ASSETS_DIR / 'scripts' / 'user_type'


GENERATED_API_DIR: Path = _env.path('GENERATED_API_DIR')
assert GENERATED_API_DIR != Path('.'), \
    'The variable "GENERATED_API_DIR" cannot be empty'


class CodeGenDstPath:
    ROOT: Path = GENERATED_API_DIR / 'assetsapi'
    TYPES: Path = ROOT / 'typesxml.py'
    ENTITIES: Path = ROOT / 'entity'

SITE_PACKAGE_DIR: Optional[Path] = _env.path('SITE_PACKAGE_DIR', None)


class EnkiPaths:
    ENKI_ROOT = Path(__file__).parent.parent.parent
    KBETYPE_DIR = ENKI_ROOT / 'enki' / 'core' / 'kbetype'
    COLLECTION_MODULE = KBETYPE_DIR / '_collection.py'
    VECTOR_MODULE = KBETYPE_DIR / '_vector.py'

    ITYPE_DIR = ENKI_ROOT / 'tools' / 'assetsapi' / 'itype'
