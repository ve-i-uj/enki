from typing import Type

from ._kbengineapi import IKBEngineLoggerModule

KBEngine: Type[IKBEngineLoggerModule] = IKBEngineLoggerModule
try:
    import KBEngine # type: ignore
except ImportError:
    pass


__all__ = [
    'KBEngine'
]
