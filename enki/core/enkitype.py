"""The application types.

* No dependences *
"""

from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Any


class EnkiType(abc.ABC):
    """Abstract class for inner implemented class of the application.

    This abstract class exists to distinguish built-in types of python
    and inner defined ones in generated code.
    """


@dataclass
class Result:
    success: bool
    result: Any
    text: str = ''


@dataclass
class AppAddr:
    """Address of a KBE component."""
    host: str
    port: int

    def copy(self) -> AppAddr:
        return AppAddr(self.host, self.port)

    def to_tuple(self) -> tuple[str, int]:
        """Возвращает адрес в виде кортежа."""
        return (self.host, self.port)

    def is_no_addr(self) -> bool:
        return self == NoValue.NO_ADDR

    def __str__(self) -> str:
        return f'{self.host}:{self.port}'


class NoValue:
    NO_ENTITY_CLS_ID = 0
    NO_ENTITY_ID = 0
    NO_ID = 0

    NO_COMPONENT_PROPERTY_ID = 0
    NO_COMPONENT_NAME = ''

    NO_POS_DIR_VALUE = -1589.123409871

    NO_ADDR = AppAddr('0.0.0.0', 0)
