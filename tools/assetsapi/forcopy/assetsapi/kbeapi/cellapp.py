from typing import Type

from ._kbengineapi import IKBEngineCellModule

KBEngine: Type[IKBEngineCellModule] = IKBEngineCellModule
try:
    import KBEngine # type: ignore
except ImportError:
    pass


__all__ = [
    'KBEngine'
]
