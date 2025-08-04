"""Адрес компонента."""

from __future__ import annotations

import typing
from dataclasses import dataclass
from typing import Final, Self, TypeAlias

Ip_addr: TypeAlias = str


class Port(int):
    """Порт."""

    def is_no_port(self) -> bool:
        """Флаг является ли значение порта отсутствием значения."""
        return self == 0

    @classmethod
    def get_no_port_obj(cls) -> Self:
        """Возвращает значение, которое является значение отсутствия порта.

        Returns:
            Self: объект отсустствия порта (ноль значение)

        """
        return cls(0)


_EMPTY_IP: Final[Ip_addr] = "0.0.0.0"  # noqa: S104
_DEFAULT_GATEWAY: Final[Ip_addr] = "0.0.0.0"  # noqa: S104
_BROADCAST_IP: Final[Ip_addr] = "255.255.255.255"


@dataclass(frozen=True)
class Addr:
    """The KBE component address."""

    ip_addr: Ip_addr
    port: Port

    # TODO: [2025-07-30 10:54 burov_alexey@mail.ru]:
    # Нужно как-то вычислять broadcast это или нет. Или может в обще не надо,
    # т.к. это нужно при вычислении обратного адреса для канала. Сперва что
    # такое бродкаст нужно разобраться
    @staticmethod
    def create_broadcast_addr(port: Port) -> Addr:
        """Создать броадкаст адрес.

        Args:
            port (Port): порт объекта адреса

        Returns:
            Addr: новый объект адреса с broadcast ip-адресом

        """
        return Addr(_BROADCAST_IP, port)

    @classmethod
    def create_default_gw_addr(cls, port: Port) -> Addr:
        """Создать адрес шлюза по умолчанию.

        Args:
            port (Port): порт объекта адреса

        Returns:
            Addr: новый объект адреса с ip-адресом "0.0.0.0"

        """
        return cls(_DEFAULT_GATEWAY, port)

    def copy(self) -> Addr:
        """Создать новый объект адреса.

        Returns:
            AppAddr: новый объект адреса

        """
        return Addr(self.ip_addr, self.port)

    def to_tuple(self) -> tuple[str, int]:
        """Возвращает адрес в виде кортежа.

        Returns:
            tuple[str, int]: кортеж из строки хоста и целого числа порта

        """
        return (str(self.ip_addr), int(self.port))

    @property
    def is_no_addr(self) -> bool:
        """Флаг, что объект - это отсутствие адреса.

        Returns:
            bool: Флаг, что объект - это отсутствие адреса.

        """
        # TODO: [2025-06-24 16:56 burov_alexey@mail.ru]:
        # Я не понял. Вроде, нигде не используется NO_ADDR. Но этот метод
        # используется. Видно бдует.
        return self.port.is_no_port()

    @property
    def is_broadcast_ip(self) -> bool:
        """Этот ip - это броадкаст адрес.

        Returns:
            bool: флаг броадкаст или нет

        """
        return self.ip_addr == _BROADCAST_IP

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, self.__class__):
            return False

        value = typing.cast("Addr", value)
        return self.ip_addr == value.ip_addr and self.port == value.port

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.ip_addr}:{self.port})"

    def __hash__(self) -> int:
        """Возвращает хэш.

        Returns:
            int: хэш

        """
        return hash(str(self))
