"""The application types."""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Any


# TODO: [2025-06-24 16:58 burov_alexey@mail.ru]:
# Нужно только EnkiType оставить здесь. Для result отдельный модуль,
# AppAddr в сеть, все NoValue в свою предметную область.

class EnkiType(ABC):
    """Abstract base class for internally implemented types in the application.

    This class serves to distinguish between Python's built-in types
    and custom types defined within the application in generated code.
    """


@dataclass
class Result:
    """Данные, описывающие удачный или неудачный результат чего бы то ни было."""

    success: bool
    result: Any
    text: str = ""


@dataclass
class AppAddr:
    """Аddress of a KBE component."""

    host: str
    port: int

    def copy(self) -> AppAddr:
        """Создать новый объект адреса."""
        return AppAddr(self.host, self.port)

    def to_tuple(self) -> tuple[str, int]:
        """Возвращает адрес в виде кортежа."""
        return (self.host, self.port)

    def is_no_addr(self) -> bool:
        # TODO: [2025-06-24 16:56 burov_alexey@mail.ru]:
        # Я не понял. Вроде, нигде не используется NO_ADDR. Но этот метод
        # используется. Видно бдует.
        return self == NoValue.NO_ADDR

    def __str__(self) -> str:
        return f"{self.host}:{self.port}"


class NoValue:
    NO_ENTITY_CLS_ID = 0
    NO_ENTITY_ID = 0
    NO_ID = 0

    NO_COMPONENT_PROPERTY_ID = 0
    NO_COMPONENT_NAME = ""

    NO_POS_DIR_VALUE = -1589.123409871

    NO_ADDR = AppAddr("0.0.0.0", 0)
