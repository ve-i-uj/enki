"""The application types."""

from __future__ import annotations

import typing
from typing import TypeAlias

HOST: TypeAlias = str
PORT: TypeAlias = int

class AppAddr:
    """Аddress of a KBE component."""

    def __init__(self, host: HOST, port: PORT) -> None:
        self._host = host
        self._port = port

    @property
    def host(self) -> HOST:
        return self._host

    @property
    def port(self) -> PORT:
        return self._port

    def copy(self) -> AppAddr:
        """Создать новый объект адреса."""
        return AppAddr(self.host, self.port)

    def to_tuple(self) -> tuple[str, int]:
        """Возвращает адрес в виде кортежа."""
        return (str(self.host), int(self.port))

    def is_no_addr(self) -> bool:
        # TODO: [2025-06-24 16:56 burov_alexey@mail.ru]:
        # Я не понял. Вроде, нигде не используется NO_ADDR. Но этот метод
        # используется. Видно бдует.
        return self == _NO_ADDR

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, self.__class__):
            return False

        value = typing.cast(AppAddr, value)
        return self.host == value.host and self.port == value.port

    def __str__(self) -> str:
        return f"{self.host}:{self.port}"

# TODO: [2025-06-25 11:42 burov_alexey@mail.ru]:
# Осталось непонятно откуда он берётся и используется ли.
_NO_ADDR = AppAddr("0.0.0.0", 0)
