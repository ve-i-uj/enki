"""Классы каналов."""

from asyncio import StreamWriter
from enki.core.enkitype import AppAddr
from enki.core.message import Message, MessageSerializer
from enki.net.client import UDPClient

from .inet import ChannelType, ConnectionInfo, IChannel


class _Channel(IChannel):

    def __init__(self, connection_info: ConnectionInfo) -> None:
        self._connection_info = connection_info

    @property
    def connection_info(self) -> ConnectionInfo:
        return self._connection_info

    def __str__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'{self._connection_info.src_addr.host}:{self._connection_info.src_addr.port} -> '
            f'{self._connection_info.dst_addr.host}:{self._connection_info.dst_addr.port})'
        )

    __repr__ = __str__


class UDPChannel(_Channel):

    def __init__(self, connection_info: ConnectionInfo) -> None:
        super().__init__(connection_info)

    @property
    def type(self) -> ChannelType:
        return ChannelType.UDP

    async def send_msg(self, msg: Message, addr: AppAddr, channel_type: ChannelType) -> bool:
        # TODO: [2023-05-15 16:44 burov_alexey@mail.ru]:
        # Создаём UDP клиент и отправляем на обратный адрес из _connection_info
        return False

    async def send_msg_content(self, data: bytes, addr: AppAddr, channel_type: ChannelType) -> bool:
        if channel_type == ChannelType.UDP:
            client = UDPClient(addr)
            await client.send(data)
            return True
        raise NotImplementedError
        return False

    async def close(self):
        pass


class TCPChannel(_Channel):

    def __init__(self, connection_info: ConnectionInfo, writer: StreamWriter) -> None:
        super().__init__(connection_info)
        self._writer = writer

    @property
    def type(self) -> ChannelType:
        return ChannelType.TCP

    async def send_msg(self, msg: Message, addr: AppAddr, channel_type: ChannelType) -> bool:
        return False

    async def send_msg_content(self, data: bytes, addr: AppAddr, channel_type: ChannelType) -> bool:
        if self._writer.is_closing():
            return False
        if addr == self._connection_info.src_addr:
            # Значит отправляем в то же tcp соединение из которого получили запрос.
            self._writer.write(data)
            await self._writer.drain()
            return True

        return False

    async def close(self):
        self._writer.close()
        await self._writer.wait_closed()
