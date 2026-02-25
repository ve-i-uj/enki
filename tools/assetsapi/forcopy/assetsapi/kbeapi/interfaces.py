
from ._kbengineapi import IKBEngineInterfacesModule

KBEngine: type[IKBEngineInterfacesModule] = IKBEngineInterfacesModule
try:
    import KBEngine  # type: ignore
except ImportError:
    pass


__all__ = [
    "KBEngine"
]
