from typing import Type

from ._kbengineapi import IKBEngineDBMgrModule

KBEngine: Type[IKBEngineDBMgrModule] = IKBEngineDBMgrModule
try:
    import KBEngine # type: ignore
except ImportError:
    pass


__all__ = [
    'KBEngine'
]
