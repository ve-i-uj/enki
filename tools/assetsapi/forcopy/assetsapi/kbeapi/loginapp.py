from typing import Type

from ._kbengineapi import IKBEngineLoginModule

KBEngine: Type[IKBEngineLoginModule] = IKBEngineLoginModule
try:
    import KBEngine # type: ignore
except ImportError:
    pass


__all__ = [
    'KBEngine'
]
