
from ._kbengineapi import IKBEngineDBMgrModule

KBEngine: type[IKBEngineDBMgrModule] = IKBEngineDBMgrModule
try:
    import KBEngine  # type: ignore
except ImportError:
    pass


__all__ = [
    "KBEngine"
]
