"""TCPClient of a KBEngine server."""

from __future__ import annotations

import abc
import asyncio
import logging
import socket
from asyncio import DatagramTransport, Future, Protocol, Transport
from typing import Callable, Optional

from enki import settings
from enki.misc import devonly
from enki.core.enkitype import Result, AppAddr
from enki.core import msgspec
from enki.core.message import Message, MsgDescr
from enki.core.message import MessageSerializer

from .inet import IClientDataReceiver, IClientMsgSender, IDataSender, \
    IMsgForwarder, IClientMsgReceiver, IServerMsgSender, IStartable

logger = logging.getLogger(__name__)


class _DefaultMsgReceiver(IClientMsgReceiver):
    """Message receiver using by default after initialization of the client."""

    def on_receive_msg(self, msg: Message) -> bool:
        logger.debug(f'[{self}] ({devonly.func_args_values()})')
        return True

    def on_end_receive_msg(self):
        logger.debug(f'[{self}] ({devonly.func_args_values()})')


class _TCPClientProtocol(Protocol):
    """

    State machine of calls:

      start -> CM [-> DR*] [-> ER?] -> CL -> end

    * CM: connection_made()
    * DR: data_received()
    * ER: eof_received()
    * CL: connection_lost()
    """

    def __init__(self, client: IClientDataReceiver):
        super().__init__()
        self._client = client
        self._transport: Optional[asyncio.Transport] = None

    def connection_made(self, transport: asyncio.Transport):
        logger.debug('[%s]', self)
        self._transport = transport

    def connection_lost(self, exc: Optional[Exception]):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._client.on_end_receive_data()

    def pause_writing(self):
        logger.warning('[%s] %s', self, devonly.func_args_values())

    def resume_writing(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())

    def data_received(self, data: bytes):
        logger.debug('[%s] %s', self, data)
        self._client.on_receive_data(memoryview(data))

    def eof_received(self) -> bool:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        return False

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'


class TCPClient(IStartable, IClientDataReceiver, IDataSender):

    def __init__(self, addr: AppAddr, on_receive_data: Callable[[bytes], None] | None = None):
        self._addr = addr
        self._transport: Optional[Transport] = None
        self._on_receive_data: Callable[[bytes], None] = \
            on_receive_data if on_receive_data is not None else lambda data: None

    @property
    def is_alive(self) -> bool:
        return self._transport is not None

    async def start(self) -> Result:
        loop = asyncio.get_running_loop()
        future = loop.create_connection(
            lambda: _TCPClientProtocol(self),
            self._addr.host, self._addr.port,
        )
        logger.info('[%s] Connecting to the server ...', self)
        try:
            self._transport, _ = await asyncio.wait_for(
                future, settings.CONNECT_TO_SERVER_TIMEOUT
            )
        except (asyncio.TimeoutError, OSError, ConnectionError) as err:
            return Result(False, None, str(err))

        logger.debug('[%s] Connected', self)
        return Result(True, None)

    def stop(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        if self._transport is None:
            logger.debug(f'[{self}] The client has already stopped')
            return
        self._transport.close()
        self._transport = None

    def on_receive_data(self, data: memoryview):
        logger.debug('[%s] Received data (%s)', self, data.obj)
        self._on_receive_data(data.tobytes())

    def on_end_receive_data(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self.stop()

    async def send(self, data: bytes) -> bool:
        if self._transport is None:
            logger.warning('[%s] The connection is not connected (data=%s)',
                           self, devonly.func_args_values())
            return False
        self._transport.write(data)
        logger.debug('[%s] Data has been sent', self)
        return True

    def __str__(self) -> str:
        return f'{__class__.__name__}({self._addr})'


class MsgTCPClient(TCPClient, IMsgForwarder, IClientMsgSender):
    """TCPClient of a KBEngine server."""

    def __init__(self, addr: AppAddr, msg_spec_by_id: dict[int, MsgDescr]):
        super().__init__(addr)
        self._serializer = MessageSerializer(msg_spec_by_id)
        self._msg_receiver = _DefaultMsgReceiver()
        self._in_buffer = b''

    def set_msg_receiver(self, receiver: IClientMsgReceiver):
        self._msg_receiver = receiver

    def on_receive_data(self, data: memoryview):
        logger.debug('[%s] Received data (%s)', self, data.obj)
        if self._in_buffer:
            # Waiting for next chunks of the message
            data = memoryview(self._in_buffer + data)
        while data:
            msg, data = self._serializer.deserialize(data)
            if msg is None:
                logger.debug('[%s] Got chunk of the message', self)
                self._in_buffer += data
                return

            logger.debug('[%s] Message "%s" fields: %s',
                         self, msg.name, msg.get_values())
            self._msg_receiver.on_receive_msg(msg)
            self._in_buffer = b''

    def on_end_receive_data(self):
        super().on_end_receive_data()
        self._msg_receiver.on_end_receive_msg()

    async def send_msg(self, msg: Message) -> bool:
        logger.debug(f'[{self}]  ({devonly.func_args_values()})')
        data = self._serializer.serialize(msg)
        return await self.send(data)


class _UDPClientProtocol(Protocol):

    def __init__(self, addr: AppAddr, data: bytes, broadcast: bool):
        self._addr = addr
        # Переменная нужна и для логики и для отображение чей это протокол в логах
        self._broadcast = broadcast
        self._data = data
        self._transport: Optional[DatagramTransport] = None

    def connection_made(self, transport: DatagramTransport):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._transport = transport
        if self._broadcast:
            self._transport.sendto(self._data, self._addr.to_tuple())
        else:
            # Если не бродкаст, значит при создании транспорта уже был передан адрес.
            self._transport.sendto(self._data)

    def error_received(self, exc):
        logger.error('[%s] %s', self, devonly.func_args_values())

    def connection_lost(self, exc):
        logger.debug('[%s] %s', self, devonly.func_args_values())

    def __str__(self) -> str:
        return f'{__class__.__name__}({self._addr}, broadcast={self._broadcast})'

    __repr__ = __str__


class UDPClient(IDataSender):

    def __init__(self, addr: AppAddr, broadcast: bool = False) -> None:
        self._addr = addr
        self._broadcast = broadcast

    async def send(self, data: bytes) -> bool:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        loop = asyncio.get_running_loop()
        if self._broadcast:
            transport, _ = await loop.create_datagram_endpoint(
                lambda: _UDPClientProtocol(self._addr, data, self._broadcast),
                family=socket.AF_INET,
                proto=socket.IPPROTO_UDP,
                allow_broadcast=True,
                local_addr=None
            )
            return True

        transport, _ = await loop.create_datagram_endpoint(
            lambda: _UDPClientProtocol(self._addr, data, self._broadcast),
            remote_addr=(self._addr.host, self._addr.port)
        )
        return True

    def __str__(self) -> str:
        return f'{__class__.__name__}({self._addr}, broadcast={self._broadcast})'

    __repr__ = __str__
