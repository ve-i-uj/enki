from typing import Type

# Импорт API модуля KBEngine для base компонента на случай разработки из IDE
from ._kbengineapi import KBEngineBaseModuleAPI

# Подсказываем Pylance, какой API имеет модуль (по факту KBEngineBaseModuleAPI - это класс).
KBEngine: Type[KBEngineBaseModuleAPI]
try:
    # Импорт модуля из движка, в случае запуска кода движком
    import KBEngine # type: ignore
except ImportError:
    # Модуля KBEngine нет в глобальном пространстве имён - значит это локальное
    # разработка из IDE.
    KBEngine = KBEngineBaseModuleAPI

__all__ = [
    'KBEngine'
]
