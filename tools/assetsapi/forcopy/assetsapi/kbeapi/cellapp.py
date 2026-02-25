
from ._kbengineapi import IKBEngineCellModule

KBEngine: type[IKBEngineCellModule] = IKBEngineCellModule
try:
    import KBEngine  # type: ignore
except ImportError:
    pass


__all__ = [
    "KBEngine"
]
