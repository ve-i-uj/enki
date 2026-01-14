"""Данные пакета транспортного уровня, извлечённые из pcap-файла."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, TypeAlias

if TYPE_CHECKING:
    from datetime import datetime
    from ipaddress import IPv4Address

logger = logging.getLogger(__name__)


Port: TypeAlias = int


class PortValue:
    """Класс для представления порта с поддержкой значения 'нет порта'."""

    # Константа класса для обозначения отсутствия порта
    _NO_PORT: ClassVar[int] = -1

    def __init__(self, value: Port) -> None:
        self._value = value

    @classmethod
    def no_port(cls) -> PortValue:
        """Создает объект без порта."""
        return cls(cls._NO_PORT)

    @property
    def is_no_port(self) -> bool:
        """Проверяет, является ли значение 'нет порта'."""
        return self._value == self._NO_PORT

    @property
    def value(self) -> Port:
        """Возвращает значение порта."""
        return self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PortValue):
            return False
        return self._value == other._value

    def __repr__(self) -> str:
        return f"PortValue({self._value})"

    def __str__(self) -> str:
        if self.is_no_port:
            return "NO_PORT"
        return str(self._value)


@dataclass
class NetChunkData:
    """Представление чанка данных из pcap-файла.

    Данные из чанка имеет начальный формат:
    Sep 19, 2025 19:03:05.867275000 +05|172.18.0.11|172.18.0.11|38048|32969|0900
    """

    time: datetime
    src: IPv4Address
    dst: IPv4Address
    tcp_src_port: PortValue
    tcp_dst_port: PortValue
    udp_src_port: PortValue
    udp_dst_port: PortValue
    data: str

    @property
    def is_udp(self) -> bool:
        return not self.udp_dst_port.is_no_port

    @property
    def is_tcp(self) -> bool:
        return not self.tcp_dst_port.is_no_port
