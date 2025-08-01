"""Информация о подключении."""

from dataclasses import dataclass

from enki.net.addr import Addr


@dataclass(frozen=True)
class ConnInfo:
    """Информация соединения (адрес клиента и сервера)."""

    # Сетевой адрес источника подключения.
    client_addr: Addr

    # Сетевой адрес соединения, к которому подключились.
    # Это адрес сервера, он есть всегда. Он задаётся в конструкторе и для
    # серверного подключения, и для клиентского подключения.
    server_addr: Addr

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"{self.client_addr.ip_addr}:{self.client_addr.port} -> "
            f"{self.server_addr.ip_addr}:{self.server_addr.port})"
        )

    __repr__ = __str__
