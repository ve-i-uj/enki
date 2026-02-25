
from ._kbengineapi import IKBEngineLoggerModule

KBEngine: type[IKBEngineLoggerModule] = IKBEngineLoggerModule
try:
    import KBEngine  # type: ignore
except ImportError:
    pass


__all__ = [
    "KBEngine"
]
