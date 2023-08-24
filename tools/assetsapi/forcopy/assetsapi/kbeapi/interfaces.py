from typing import Type

from ._kbengineapi import IKBEngineInterfacesModule

KBEngine: Type[IKBEngineInterfacesModule] = IKBEngineInterfacesModule
try:
    import KBEngine # type: ignore
except ImportError:
    pass


__all__ = [
    'KBEngine'
]
