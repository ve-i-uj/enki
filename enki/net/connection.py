"""Классы отвечающие непосредственно за то _как_ происходит сетевое подключение."""

from __future__ import annotations

import abc
import asyncio
from functools import cached_property
import logging
from typing import Any, Optional

from enki import settings
from enki.misc import devonly
from enki.core.enkitype import Result, AppAddr
from enki.core.message import MessageSerializer, MsgDescr

from .inet import ConnectionInfo, IClientDataReceiver, ITCPClient, ITCPConnection


logger = logging.getLogger(__name__)


class _TCPClientProtocol(asyncio.Protocol):
    """

    State machine of calls:

      start -> CM [-> DR*] [-> ER?] -> CL -> end

    * CM: connection_made()
    * DR: data_received()
    * ER: eof_received()
    * CL: connection_lost()
    """

    def __init__(self, connection: TCPClientConnection):
        super().__init__()
        self._connection = connection
        self._transport: Optional[asyncio.Transport] = None

    def connection_made(self, transport: asyncio.Transport):
        logger.info('[%s]', self)
        self._transport = transport

    def connection_lost(self, exc: Optional[Exception]):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._connection.on_end_receive_data()

    def pause_writing(self):
        logger.warning('[%s] %s', self, devonly.func_args_values())

    def resume_writing(self):
        logger.info('[%s] %s', self, devonly.func_args_values())

    def data_received(self, data: bytes):
        logger.debug('[%s] %s', self, data)
        self._connection.on_receive_data(memoryview(data))

    def eof_received(self) -> bool:
        logger.info('[%s] %s', self, devonly.func_args_values())
        # If this returns a false value (including None), the transport will close itself.
        return False

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'


class TCPClientConnection(ITCPConnection):
    """The client tcp connection to a KBE component."""

    def __init__(self, addr: AppAddr, client: ITCPClient):
        self._dst_addr = addr
        self._client = client

        self._transport: Optional[asyncio.Transport] = None
        logger.debug('[%s] Initialized', self)

    @property
    def connection_info(self) -> ConnectionInfo:
        if self._transport is None:
            src_address = None
        else:
            sock = self._transport.get_extra_info('socket')
            src_address = AppAddr(*sock.getpeername())
        return ConnectionInfo(src_address, self._dst_addr)

    @property
    def is_alive(self) -> bool:
        return self._transport is not None

    @property
    def can_send(self) -> bool:
        return self.is_alive

    async def send(self, data: bytes) -> bool:
        """Send data to the server."""
        if self._transport is None:
            logger.warning('[%s] The connection is not connected (data=%s)',
                           self, devonly.func_args_values())
            return False
        self._transport.write(data)
        logger.debug('[%s] Data has been sent', self)
        return True

    def on_receive_data(self, data: memoryview):
        self._client.on_receive_data(data)

    def on_end_receive_data(self):
        self._transport = None

    async def connect(self) -> Result:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        loop = asyncio.get_running_loop()
        future = loop.create_connection(
            lambda: _TCPClientProtocol(self),
            self._dst_addr.host, self._dst_addr.port,
        )
        logger.info('[%s] Connecting to the server ...', self)
        try:
            self._transport, self._protocol = await asyncio.wait_for(
                future, settings.CONNECT_TO_SERVER_TIMEOUT
            )
        except (asyncio.TimeoutError, OSError, ConnectionError) as err:
            return Result(False, None, str(err))

        logger.debug('[%s] Connected', self)
        return Result(True, None)

    def close(self):
        """Close the active connection."""
        logger.debug('[%s]', self)
        if self._transport is None:
            return
        self._transport.close()
        self._transport = None
        self._protocol = None
        logger.debug('[%s] The transport in closing ...', self)

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self._dst_addr})'
