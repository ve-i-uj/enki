"""Интерфейсы ключевых сервеных типов для скриптов в assets'ах.

Этот модуль будет копироваться в игровые assets'ы, поэтому он должен содержать
только Python импорты.
"""

from __future__ import annotations

import abc
import logging
from dataclasses import dataclass
from typing import Any, Callable, ClassVar, Optional

logger = logging.getLogger(__name__)


@dataclass
class GDInfoDC:
    """Parent class for the GD info."""
    pass


class IGDAccessor(abc.ABC):
    """Интерфейс класса имеющего доступ к KBEngine.globalData ."""

    GD_KEY: ClassVar[str]

    @abc.abstractmethod
    def get(self, uid: str) -> Optional[GDInfoDC]:
        pass

    @abc.abstractmethod
    def add(self, info_dc: GDInfoDC) -> str:
        """Returns unique identifier."""
        pass

    @abc.abstractmethod
    def remove(self, uid: str) -> bool:
        pass
