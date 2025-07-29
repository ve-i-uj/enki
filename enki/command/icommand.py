"""Интерфейс команды в кластере KBEngine."""

from __future__ import annotations

import abc
import logging
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from enki.misc.result import Result

logger = logging.getLogger(__name__)

TIMEOUT_ERROR_MSG = "Timeout Error"


@dataclass
class CommandResult(Result):
    """Результат выполнения команды."""

    success: bool
    result: Any = None
    text: str = ""


_R = TypeVar("_R", bound=CommandResult)


class ICommand(abc.ABC, Generic[_R]):
    """Интерфейс команды."""

    @abc.abstractmethod
    async def execute(self) -> _R:
        """Выполнить команду."""

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"
