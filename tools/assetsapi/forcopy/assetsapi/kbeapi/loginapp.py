
from ._kbengineapi import IKBEngineLoginModule

KBEngine: type[IKBEngineLoginModule] = IKBEngineLoginModule
try:
    import KBEngine  # type: ignore
except ImportError:
    pass


__all__ = [
    "KBEngine"
]
