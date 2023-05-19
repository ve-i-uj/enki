"""TCPClient of a KBEngine server."""

from __future__ import annotations

import abc
import asyncio
import logging
from asyncio import DatagramTransport, Future, Protocol, Transport
from typing import Optional
from enki import settings

from enki.misc import devonly
from enki.core.enkitype import Result, AppAddr
from enki.core import msgspec
from enki.core.message import Message, MsgDescr
from enki.net.inet import IClientMsgReceiver
from enki.core.message import MessageSerializer

from .inet import IClientDataReceiver, IDataSender, ITCPClient

logger = logging.getLogger(__name__)


class _DefaultMsgReceiver(IClientMsgReceiver):
    """Message receiver using by default after initialization of the client."""

    def on_receive_msg(self, msg: Message) -> bool:
        logger.debug(f'[{self}] ({devonly.func_args_values()})')
        return True

    def on_end_receive_msg(self):
        pass


class _TCPClientProtocol(Protocol):
    """

    State machine of calls:

      start -> CM [-> DR*] [-> ER?] -> CL -> end

    * CM: connection_made()
    * DR: data_received()
    * ER: eof_received()
    * CL: connection_lost()
    """

    def __init__(self, client: TCPClient):
        super().__init__()
        self._client = client
        self._transport: Optional[asyncio.Transport] = None

    def connection_made(self, transport: asyncio.Transport):
        logger.info('[%s]', self)
        self._transport = transport

    def connection_lost(self, exc: Optional[Exception]):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._client.on_end_receive_data()

    def pause_writing(self):
        logger.warning('[%s] %s', self, devonly.func_args_values())

    def resume_writing(self):
        logger.info('[%s] %s', self, devonly.func_args_values())

    def data_received(self, data: bytes):
        logger.debug('[%s] %s', self, data)
        self._client.on_receive_data(memoryview(data))

    def eof_received(self) -> bool:
        logger.info('[%s] %s', self, devonly.func_args_values())
        # If this returns a false value (including None), the transport will close itself.
        return False

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'


class TCPClient(ITCPClient, IClientDataReceiver):
    """TCPClient of a KBEngine server."""

    def __init__(self, addr: AppAddr, msg_spec_by_id: dict[int, MsgDescr]):
        self._addr = addr
        self._serializer = MessageSerializer(msg_spec_by_id)
        self._msg_receiver = _DefaultMsgReceiver()

        self._transport: Optional[Transport] = None
        self._in_buffer = b''

    @property
    def is_alive(self) -> bool:
        return self._transport is not None

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
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self.stop()
        self._msg_receiver.on_end_receive_msg()

    async def send_msg(self, msg: Message) -> bool:
        logger.debug(f'[{self}]  ({devonly.func_args_values()})')
        data = self._serializer.serialize(msg)
        if self._transport is None:
            logger.warning('[%s] The connection is not connected (data=%s)',
                           self, devonly.func_args_values())
            return False
        self._transport.write(data)
        logger.debug('[%s] Data has been sent', self)
        return True

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

    def __str__(self) -> str:
        return f'{__class__.__name__}({self._addr})'


class StreamClient(TCPClient):
    """Клиент который в ответ на отправленное сообщение получает стрим."""

    def __init__(self, addr: AppAddr, msg_spec_by_id: dict[int, MsgDescr]):
        super().__init__(addr, msg_spec_by_id)
        self._resp_msg_spec = msgspec.fakeMsgDescr

    def set_resp_msg_spec(self, resp_msg_spec: MsgDescr):
        self._resp_msg_spec = resp_msg_spec

    def on_receive_data(self, data: memoryview):
        while data:
            fields = []
            for kbe_type in self._resp_msg_spec.field_types:
                value, size = kbe_type.decode(data)
                fields.append(value)
                data = data[size:]

            resp_msg = Message(self._resp_msg_spec, tuple(fields))
            self._msg_receiver.on_receive_msg(resp_msg)


class _UDPClientProtocol(Protocol):

    def __init__(self, addr: AppAddr, data: bytes):
        self._addr = addr
        self._data = data
        self._transport: Optional[DatagramTransport] = None

    def connection_made(self, transport: DatagramTransport):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._transport = transport
        self._transport.sendto(self._data)

    def error_received(self, exc):
        logger.error('[%s] %s', self, devonly.func_args_values())

    def connection_lost(self, exc):
        logger.debug('[%s] %s', self, devonly.func_args_values())

    def __str__(self) -> str:
        return f'{__class__.__name__}({self._addr})'

    __repr__ = __str__


class UDPClient(IDataSender):

    def __init__(self, addr: AppAddr) -> None:
        self._addr = addr

    async def send(self, data: bytes) -> bool:
        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: _UDPClientProtocol(self._addr, data),
            remote_addr=(self._addr.host, self._addr.port)
        )
        return True

    def __str__(self) -> str:
        return f'{__class__.__name__}({self._addr})'

    __repr__ = __str__
