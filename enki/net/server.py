"""Модуль содержит классы серверов, обслуживающих сетевые соединения."""

from __future__ import annotations

import asyncio
import logging
from asyncio import DatagramProtocol, DatagramTransport
import struct
from typing import Optional
from enki.core.message import MessageSerializer, MsgDescr

from enki.misc import devonly
from enki.core.enkitype import AppAddr, Result
from enki.net.channel import UDPChannel
from enki.net.inet import ConnectionInfo, IChannel, IMsgSender, IServer, \
    IServerDataReceiver, IServerMsgReceiver

logger = logging.getLogger(__name__)


class UDPServerProtocol(DatagramProtocol):

    def __init__(self, data_receiver: UDPServer):
        super().__init__()
        self._data_receiver = data_receiver
        self._transport: Optional[DatagramTransport] = None

    def connection_made(self, transport: DatagramTransport):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._transport = transport

    def connection_lost(self, exc):
        logger.info('[%s] %s', self, exc)
        if exc is not None:
            self._data_receiver.stop()

    def datagram_received(self, data: bytes, addr: tuple[str, int]):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._data_receiver.on_receive_data(memoryview(data), addr)

    def error_received(self, exc):
        logger.error(str(exc))

    def __str__(self) -> str:
        return f'{__class__.__name__}()'


class UDPServer(IServer, IServerDataReceiver):

    def __init__(self, addr: AppAddr, msg_spec_by_id: dict[int, MsgDescr],
                 msg_receiver: IServerMsgReceiver):
        self._addr = addr
        self._transport: Optional[DatagramTransport] = None
        self._serializer = MessageSerializer(msg_spec_by_id)
        self._msg_receiver = msg_receiver

    async def start(self) -> Result:
        loop = asyncio.get_running_loop()
        try:
            self._transport, _ = await loop.create_datagram_endpoint(
                lambda: UDPServerProtocol(data_receiver=self),
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

    @property
    def is_alive(self) -> bool:
        return self._transport is not None

    def on_receive_data(self, data: memoryview, addr: tuple[str, int]):
        logger.debug('[%s] Received data (%s)', self, data.obj)
        conn_info = ConnectionInfo(AppAddr(addr[0], addr[1]), self._addr)
        channel = UDPChannel(conn_info)

        err_template = '[%s] Got unreadable data. Rejected'
        while data:
            try:
                msg, data = self._serializer.deserialize(data)
            except (KeyError, struct.error):
                logger.warning(err_template, self)
                return
            if msg is None:
                logger.warning(err_template, self)
                return
            logger.debug('[%s] Message "%s" fields: %s', self, msg.name, msg.get_values())
            self._msg_receiver.on_receive_msg(msg, channel)
            self._in_buffer = b''


    def __str__(self) -> str:
        return f'{__class__.__name__}()'
