"""Класс результата для чего либо."""

from dataclasses import dataclass
from typing import Any


@dataclass
class Result:
    """Данные, описывающие удачный или неудачный результат."""

    success: bool
    result: Any
    text: str = ""
