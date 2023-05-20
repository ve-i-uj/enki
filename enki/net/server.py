"""Модуль содержит классы серверов, обслуживающих сетевые соединения."""

from __future__ import annotations

import asyncio
import logging
from asyncio import DatagramProtocol, DatagramTransport, Protocol, Server, StreamReader, StreamWriter, Task, Transport
import socket
import struct
from typing import Optional
from enki import settings
from enki.core.message import Message, MessageSerializer, MsgDescr

from enki.misc import devonly
from enki.core.enkitype import AppAddr, Result
from enki.net.channel import TCPChannel, UDPChannel
from enki.net.inet import ConnectionInfo, IChannel, IDataSender, IServer, \
    IServerDataReceiver, IServerMsgReceiver

logger = logging.getLogger(__name__)


def get_free_port() -> int:
    sock = socket.socket()
    sock.bind(('', 0))
    return sock.getsockname()[1]


def get_real_host_ip(docker_container_name: str) -> str:
    """По имени контейнера получить его реальный ip адрес."""
    sock = socket.socket()
    sock.bind((docker_container_name, 0))
    return sock.getsockname()[0]


class UDPServerProtocol(DatagramProtocol):

    def __init__(self, addr, data_receiver: IServerDataReceiver):
        self._addr = addr
        self._data_receiver = data_receiver
        self._transport: Optional[DatagramTransport] = None

    def connection_made(self, transport: DatagramTransport):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._transport = transport

    def connection_lost(self, exc):
        logger.info('[%s] %s', self, exc)
        if exc is not None:
            self._data_receiver.on_stop_receive()

    def datagram_received(self, data: bytes, addr: tuple[str, int]):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        asyncio.create_task(self._data_receiver.on_receive_data(
            memoryview(data), AppAddr(*addr))
        )

    def error_received(self, exc):
        logger.error(str(exc))

    def __str__(self) -> str:
        return f'{__class__.__name__}(addr={self._addr})'

    __repr__ = __str__


class UDPServer(IServer, IServerDataReceiver):

    def __init__(self, addr: AppAddr):
        self._addr = addr
        self._transport: Optional[DatagramTransport] = None

    async def start(self) -> Result:
        loop = asyncio.get_running_loop()
        try:
            self._transport, _ = await loop.create_datagram_endpoint(
                lambda: UDPServerProtocol(self._addr, data_receiver=self),
                local_addr=(self._addr.host, self._addr.port)
            )
        except (asyncio.TimeoutError, OSError, ConnectionError) as err:
            return Result(False, None, str(err))

        logger.debug('[%s] Connected', self)
        return Result(True, None)

    def stop(self):
        if self._transport is None:
            logger.warning('[%s] The server has been already stopped', self)
            return
        self._transport.close()

    def on_stop_receive(self):
        self.stop()

    @property
    def is_alive(self) -> bool:
        return self._transport is not None

    async def on_receive_data(self, data: memoryview, addr: AppAddr):
        logger.debug('[%s] Received data (%s)', self, data.obj)

    def __str__(self) -> str:
        return f'{__class__.__name__}(addr={self._addr})'

    __repr__ = __str__


class UDPMsgServer(UDPServer):
    """Сервер принимает по UDP закодированные сообщения."""

    def __init__(self, addr: AppAddr, msg_spec_by_id: dict[int, MsgDescr],
                 msg_receiver: IServerMsgReceiver):
        super().__init__(addr)
        self._serializer = MessageSerializer(msg_spec_by_id)
        self._msg_receiver = msg_receiver

    async def on_receive_data(self, data: memoryview, addr: AppAddr):
        logger.debug('[%s] Received data (%s)', self, data.obj)
        conn_info = ConnectionInfo(addr, self._addr)
        channel = UDPChannel(conn_info)

        err_template = '[%s] Got unreadable data. Rejected'
        while data:
            try:
                msg, data = self._serializer.deserialize(data)
            except KeyError:
                logger.warning(err_template, self)
                return
            if msg is None:
                logger.warning(err_template, self)
                return
            logger.debug('[%s] Message "%s" fields: %s', self, msg.name, msg.get_values())
            await self._msg_receiver.on_receive_msg(msg, channel)


class TCPServer(IServer, IDataSender):

    def __init__(self, addr: AppAddr, msg_spec_by_id: dict[int, MsgDescr],
                 msg_receiver: IServerMsgReceiver):
        self._addr = addr
        self._transport: Optional[Transport] = None
        self._serializer = MessageSerializer(msg_spec_by_id)
        self._msg_receiver = msg_receiver
        self._server: Optional[Server] = None
        self._serve_forever_task: Optional[Task] = None

    async def start(self) -> Result:
        try:
            self._server = await asyncio.start_server(
                self.handle_connection, self._addr.host, self._addr.port
            )
        except (asyncio.TimeoutError, OSError, ConnectionError) as err:
            return Result(False, None, str(err))

        async def serve_forever(server: Server):
            await server.start_serving()

        self._serve_forever_task = asyncio.create_task(serve_forever(self._server))

        return Result(True, None)

    async def handle_connection(self, reader: StreamReader, writer: StreamWriter):
        addr = writer.get_extra_info('peername')
        conn_info = ConnectionInfo(AppAddr(addr[0], addr[1]), self._addr)
        channel = TCPChannel(conn_info, writer)

        buffer = bytes()
        while not reader.at_eof():
            data = await reader.read(settings.TCP_CHUNK_SIZE)
            if not data:
                continue
            if buffer:
                data = buffer + data
            msg, data_tail = self._serializer.deserialize(memoryview(data))
            if msg is None:
                logger.info(f'[{self}] Data cannot be decoded to the message (%s)',
                            self, data)
                buffer = data
                continue
            buffer = data_tail.tobytes()
            logger.debug('[%s] Message "%s" fields: %s', self, msg.name, msg.get_values())
            await self._msg_receiver.on_receive_msg(msg, channel)

    async def stop(self):
        if self._server is None:
            logger.warning('[%s] The server has been already stopped', self)
            return
        self._server.close()
        await self._server.wait_closed()
        self._server = None
        assert self._serve_forever_task is not None
        self._serve_forever_task.cancel()

    @property
    def is_alive(self) -> bool:
        return self._server is not None

    def send(self, data: bytes) -> bool:
        return False

    def __str__(self) -> str:
        return f'{__class__.__name__}()'
