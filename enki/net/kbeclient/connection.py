"""Different connections to the KBEngine server.

* No dependences *
"""

from __future__ import annotations

import abc
import asyncio
import logging
from typing import Any, Optional

from enki import settings
from enki import devonly
from enki.enkitype import Result


logger = logging.getLogger(__name__)


class IDataReceiver(abc.ABC):

    @abc.abstractmethod
    def on_receive_data(self, data: memoryview) -> None:
        """Handle incoming bytes data from the server."""
        pass

    @abc.abstractmethod
    def on_end_receive_data(self):
        """No more data after this callback called."""
        pass


class TCPClientProtocol(asyncio.Protocol):
    """

    State machine of calls:

      start -> CM [-> DR*] [-> ER?] -> CL -> end

    * CM: connection_made()
    * DR: data_received()
    * ER: eof_received()
    * CL: connection_lost()
    """

    _NO_TRANSPORT = asyncio.Transport()

    def __init__(self, data_receiver: IDataReceiver):
        super().__init__()

        self._data_receiver = data_receiver
        self._transport: asyncio.Transport = self._NO_TRANSPORT

    def connection_made(self, transport: asyncio.Transport):
        logger.info('[%s]', self)
        self._transport = transport

    def connection_lost(self, exc: Optional[Exception]):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        if exc is None:
            # a regular EOF is received or the connection was aborted or closed
            pass
        self._data_receiver.on_end_receive_data()

    def pause_writing(self):
        logger.warning('[%s] %s', self, devonly.func_args_values())

    def resume_writing(self):
        logger.info('[%s] %s', self, devonly.func_args_values())

    def data_received(self, data: bytes):
        logger.debug('[%s] %s', self, data)
        self._data_receiver.on_receive_data(memoryview(data))

    def eof_received(self) -> bool:
        logger.info('[%s] %s', self, devonly.func_args_values())
        # If this returns a false value (including None), the transport will close itself.
        return False

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'


class ConnectResult(Result):
    @property
    def success(self) -> bool:
        return None

    @property
    def result(self) -> Any:
        return None

    @property
    def text(self) -> str:
        return None



class AppConnection:
    """The connection to a KBE component."""

    _NO_TRANSPORT = asyncio.Transport()
    _NO_PROTOCOL = asyncio.Protocol()

    def __init__(self, host: str, port: int, data_receiver: IDataReceiver):
        self._host: str = host
        self._port: int = port
        self._data_receiver = data_receiver

        self._transport: asyncio.Transport = self._NO_TRANSPORT
        self._protocol: TCPClientProtocol = self._NO_PROTOCOL  # type: ignore

        self._stopping: bool = False
        self._closed: bool = True
        logger.debug('[%s] Initialized', self)

    async def connect(self) -> ConnectResult:
        """Connect to the KBE server."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        loop = asyncio.get_running_loop()
        future = loop.create_connection(
            lambda: TCPClientProtocol(self._data_receiver), self._host, self._port,
        )
        logger.info('[%s] Connecting to the server ...', self)
        try:
            self._transport, self._protocol = await asyncio.wait_for(  # type: ignore
                future, settings.CONNECT_TO_SERVER_TIMEOUT
            )
        except (asyncio.TimeoutError, OSError, ConnectionError) as err:
            return ConnectResult(False, None, str(err))

        self._closed = False
        logger.debug('[%s] Connected', self)
        return ConnectResult(True, None)

    async def send(self, data: bytes):
        """Send data to the server."""
        assert self._transport is not self._NO_TRANSPORT
        self._transport.write(data)
        logger.debug('[%s] Data has been sent', self)

    def close(self):
        """Close the active connection."""
        logger.debug('[%s]', self)
        if self._closed:
            return

        assert self._transport is not self._NO_TRANSPORT

        self._stopping = True
        self._transport.close()
        self._closed = True
        self._transport = self._NO_TRANSPORT
        self._protocol = self._NO_PROTOCOL  # type: ignore
        logger.debug('[%s] The transport in closing ...', self)

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self._host}, {self._port})'
