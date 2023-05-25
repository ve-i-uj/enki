"""Классы каналов."""

import logging

from asyncio import StreamWriter

from enki.misc import devonly
from enki.core.enkitype import AppAddr
from enki.core.message import Message
from enki.net.client import UDPClient

from .inet import ChannelType, ConnectionInfo, IChannel, IServerMsgSender

logger = logging.getLogger(__name__)


class Channel(IChannel, IServerMsgSender):

    def __init__(self, connection_info: ConnectionInfo) -> None:
        self._connection_info = connection_info

    @property
    def connection_info(self) -> ConnectionInfo:
        return self._connection_info

    async def send_msg(self, msg: Message, addr: AppAddr, channel_type: ChannelType) -> bool:
        raise NotImplementedError

    async def send_msg_content(self, data: bytes, addr: AppAddr, channel_type: ChannelType) -> bool:
        raise NotImplementedError

    def __str__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'{self._connection_info.src_addr.host}:{self._connection_info.src_addr.port} -> '
            f'{self._connection_info.dst_addr.host}:{self._connection_info.dst_addr.port})'
        )

    __repr__ = __str__


class UDPChannel(Channel):

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
        logger.debug('[%s] %s', self, devonly.func_args_values())
        if channel_type == ChannelType.UDP:
            client = UDPClient(addr)
            await client.send(data)
            return True
        if channel_type == ChannelType.BROADCAST:
            client = UDPClient(addr, broadcast=True)
            await client.send(data)
            return True
        raise NotImplementedError
        return False

    async def close(self):
        pass


class TCPChannel(Channel, IServerMsgSender):

    def __init__(self, connection_info: ConnectionInfo, writer: StreamWriter) -> None:
        super().__init__(connection_info)
        self._writer = writer

    @property
    def type(self) -> ChannelType:
        return ChannelType.TCP

    async def send_msg(self, msg: Message, addr: AppAddr, channel_type: ChannelType) -> bool:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        return False

    async def send_msg_content(self, data: bytes, addr: AppAddr, channel_type: ChannelType) -> bool:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        if self._writer.is_closing():
            return False
        if addr == self._connection_info.src_addr:
            # Значит отправляем в то же tcp соединение из которого получили запрос.
            self._writer.write(data)
            await self._writer.drain()
            return True

        return False

    async def close(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._writer.close()
        await self._writer.wait_closed()
