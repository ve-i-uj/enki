"""The application types.

* No dependences *
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


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

    def __str__(self) -> str:
        return f'{self.host}:{self.port}'


class NoValue:
    NO_ENTITY_CLS_ID = 0
    NO_ENTITY_ID = 0
    NO_ID = 0

    NO_COMPONENT_PROPERTY_ID = 0
    NO_COMPONENT_NAME = ''

    NO_POS_DIR_VALUE = -1589.123409871
