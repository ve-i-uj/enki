"""The application types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Result:
    """Данные, описывающие удачный или неудачный результат чего бы то ни было."""

    success: bool
    result: Any
    text: str = ""


class NoValue:
    NO_ENTITY_CLS_ID = 0
    NO_ENTITY_ID = 0
    NO_ID = 0

    NO_COMPONENT_PROPERTY_ID = 0
    NO_COMPONENT_NAME = ""

    NO_POS_DIR_VALUE = -1589.123409871
