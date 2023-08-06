from typing import Type

from ._kbengineapi import KBEngineCellModuleAPI

KBEngine: Type[KBEngineCellModuleAPI]
try:
    import KBEngine # type: ignore
except ImportError:
    KBEngine = KBEngineCellModuleAPI


__all__ = [
    'KBEngine'
]
