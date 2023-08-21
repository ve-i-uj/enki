import logging
from pathlib import Path
from typing import Optional

import environs

_env = environs.Env()

LOG_LEVEL: int = _env.log_level('LOG_LEVEL', logging.INFO)

# Будет сгенерирован (скопирован по факту) только API для модуля KBEngine, API
# сущностей и типы генерироваться не будут
ONLY_KBENGINE_API: bool = _env.bool('ONLY_KBENGINE_API', False)

# Если выставлена эта переменная, то ещё будут скопированы интерфейсы, классы
# и ряд полезных для разработки функций
ADD_ASSETSTOOLS: bool = _env.bool('ADD_ASSETSTOOLS', False)
ADD_TYPING_EXTENSIONS_LIB: bool = _env.bool('ADD_TYPING_EXTENSIONS_LIB', True)

# Директория расположения шаблонов для генерации кода
class Templates:
    _jinja_templs_dir: Path = Path(__file__).parent / 'templates'
    TYPESXML_JINJA_TEMPLATE_PATH = _jinja_templs_dir / 'typesxml.py.jinja'
    ENTITY_JINJA_TEMPLATE_PATH = _jinja_templs_dir / 'entity.py.jinja'
    COMPONENT_JINJA_TEMPLATE_PATH = _jinja_templs_dir / 'entitycomponent.py.jinja'
    USER_TYPE_PATH = _jinja_templs_dir / 'user_type.py.jinja'

GAME_ASSETS_DIR: Path = _env.path('GAME_ASSETS_DIR')
assert GAME_ASSETS_DIR != Path('.'), 'The variable "GAME_ASSETS_DIR" cannot be empty'


class AssetsDirs:
    ENTITIES_XML_PATH: Path = GAME_ASSETS_DIR / 'scripts' / 'entities.xml'
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
    TYPESXML_WITHOUT_CONVERTERS: Path = USER_TYPE_DIR / '_typesxml.py'
    ENTITIES: Path = ASSETSAPI_DIR / 'entity'
    INTERFACES: Path = ASSETSAPI_DIR / 'interfaces'
    COMPONENTS: Path = ASSETSAPI_DIR / 'components'
    TYPING_EXTENSIONS_PATH: Path = AssetsDirs.SERVER_COMMON / 'typing_extensions.py'

# Если в user_type используются сторонние библиотеки, то их нужно добавить
# через переменную SITE_PACKAGES_DIR. Это должна быть папка с библиотеками Python.
SITE_PACKAGES_DIR: Optional[Path] = _env.path('SITE_PACKAGES_DIR', None)


class EnkiPaths:
    ENKI_ROOT: Path = Path(__file__).parent.parent.parent
    FORCOPY_DIR = ENKI_ROOT / 'tools' / 'assetsapi' / 'forcopy'
    ASSETSAPI_FOR_COPY_DIR = FORCOPY_DIR / 'assetsapi'
    ASSETSTOOLS_FOR_COPY_DIR = FORCOPY_DIR / 'assetstools'
    TYPING_EXTENSIONS_PATH = FORCOPY_DIR / 'typing_extensions.py'

# Proxy сущности через запятую без пробелов. Указанным сущсностям при генерации
# их API унаследуют в этом случае KBEngine.Proxy . Это нужно, т.к. некоторые
# методы ожидают в аргументе Proxy, но Proxy будет сущность или нет можно узнать только
# в рантайме, когда сущность наследует KBEngine.Proxy. При генерации кода по
# конфигам узнать это возможности нет, поэтому нужно указывать в ручную.
_proxy_entities = _env.str('PROXY_ENTITIES', '').split(',')
PROXY_ENTITIES: list[str] = [] if _proxy_entities == [''] else _proxy_entities

# Использовать комментарии в def файле, как имена параметров при таком описании:
#
# <ClientMethods>
#     <resp_get_avatars>
#         <Arg> AVATAR_INFOS </Arg> <!-- parameter_name -->
#     </resp_get_avatars>
# </ClientMethods>
#
# Эта переменная нужна, чтобы иметь возможность отключить такой подход, если,
# например, комментарии уже существуют.
USE_DEF_COMMENTS_LIKE_PARAMS: bool = _env.bool('USE_DEF_COMMENTS_LIKE_PARAMS', True)
