"""Данные пакета транспортного уровня, извлечённые из pcap-файла."""

import logging
from dataclasses import dataclass
from datetime import datetime
from ipaddress import IPv4Address
from typing import TypeAlias

logger = logging.getLogger(__name__)


Port: TypeAlias = int


@dataclass
class NetChunkData:
    """Представление чанка данных из pcap-файла.

    Данные из чанка имеет начальный формат:
    Sep 19, 2025 19:03:05.867275000 +05|172.18.0.11|172.18.0.11|38048|32969|0900
    """

    time: datetime
    src: IPv4Address
    dst: IPv4Address
    tcp_src_port: Port
    tcp_dst_port: Port
    udp_src_port: Port
    udp_dst_port: Port
    data: str
