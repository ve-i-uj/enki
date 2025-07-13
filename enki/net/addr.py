"""Адрес компонента."""

from __future__ import annotations

import typing
from dataclasses import dataclass
from typing import Final, TypeAlias

Host: TypeAlias = str
Port: TypeAlias = int

_EMPTY_IP: Final[Host] = "0.0.0.0"  # noqa: S104
_BROADCAST_IP: Final[Host] = "255.255.255.255"
_NO_PORT: Final[Port] = 0

@dataclass(frozen=True)
class Addr:
    """The KBE component address."""

    host: Host
    port: Port

    @staticmethod
    def create_broadcast_addr(port: Port) -> Addr:
        """Создать броадкаст адрес.

        Args:
            port (Port): порт объекта адреса

        Returns:
            Addr: новый объект адреса с broadcast ip-адресом

        """
        return Addr(_BROADCAST_IP, port)

    def copy(self) -> Addr:
        """Создать новый объект адреса.

        Returns:
            AppAddr: новый объект адреса

        """
        return Addr(self.host, self.port)

    def to_tuple(self) -> tuple[Host, Port]:
        """Возвращает адрес в виде кортежа.

        Returns:
            tuple[Host, Port]: кортеж из строки хоста и целого числа порта

        """
        return (str(self.host), int(self.port))

    @property
    def is_no_addr(self) -> bool:
        """Флаг, что объект - это отсутствие адреса.

        Returns:
            bool: Флаг, что объект - это отсутствие адреса.

        """
        # TODO: [2025-06-24 16:56 burov_alexey@mail.ru]:
        # Я не понял. Вроде, нигде не используется NO_ADDR. Но этот метод
        # используется. Видно бдует.
        return self.host == _EMPTY_IP and self.port == _NO_PORT

    @property
    def is_broadcast_ip(self) -> bool:
        """Этот ip - это броадкаст адрес.

        Returns:
            bool: флаг броадкаст или нет

        """
        return self.host == _BROADCAST_IP

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, self.__class__):
            return False

        value = typing.cast("Addr", value)
        return self.host == value.host and self.port == value.port

    def __str__(self) -> str:
        return f"{self.host}:{self.port}"

    def __hash__(self) -> int:
        """Возвращает хэш.

        Returns:
            int: хэш

        """
        return hash(str(self))
