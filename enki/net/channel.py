"""Классы каналов."""

from enki.core.enkitype import AppAddr
from enki.core.message import Message

from .inet import ConnectionInfo, IChannel


class UDPChannel(IChannel):

    def __init__(self, connection_info: ConnectionInfo) -> None:
        self._connection_info = connection_info

    @property
    def connection_info(self) -> ConnectionInfo:
        return self._connection_info

    def send_msg(self, msg: Message) -> bool:
        # TODO: [2023-05-15 16:44 burov_alexey@mail.ru]:
        # Создаём UDP клиент и отправляем на обратный адрес из _connection_info
        return False

    def send_msg_content(self, msg: Message) -> bool:
        return False

    def __str__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'{self._connection_info.src_addr.host}:{self._connection_info.src_addr.port} -> '
            f'{self._connection_info.dst_addr.host}:{self._connection_info.dst_addr.port})'
        )

    __repr__ = __str__
