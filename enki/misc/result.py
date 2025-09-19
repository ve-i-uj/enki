"""Класс результата для чего либо."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Result:
    """Объект результата выполенения чего-либо."""

    success: bool
    result: Any
    text: str = ""
