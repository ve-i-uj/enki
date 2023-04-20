"""The application types.

* No dependences *
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Result:
    @property
    def success(self) -> bool:
        return None

    @property
    def result(self) -> Any:
        return None

    @property
    def text(self) -> str:
        return None



@dataclass
class AppAddr:
    """Address of a KBE component."""
    @property
    def host(self) -> str:
        return None

    @property
    def port(self) -> int:
        return None


    def __str__(self) -> str:
        return f'{self.host}:{self.port}'
