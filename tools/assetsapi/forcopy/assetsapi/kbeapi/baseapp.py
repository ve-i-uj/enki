from typing import Type

# Импорт интерфейса модуля KBEngine для base компонента на случай разработки из IDE
from ._kbengineapi import IKBEngineBaseModule

# Подсказываем Pylance, какой интерфейс имеет модуль (по факту IKBEngineBaseModule - это класс).
KBEngine: Type[IKBEngineBaseModule] = IKBEngineBaseModule
try:
    # Импорт модуля из движка, в случае запуска кода движком
    import KBEngine # type: ignore
except ImportError:
    # Модуля KBEngine нет в глобальном пространстве имён - значит это локальное
    # разработка из IDE.
    pass

__all__ = [
    'KBEngine'
]
