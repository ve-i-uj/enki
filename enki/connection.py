"""Different connections to the KBEngine server."""

from __future__ import annotations
import abc
import asyncio
import logging

from tornado import tcpclient
from tornado import iostream

from enki import client

logger = logging.getLogger(__name__)


class IConnection(abc.ABC):

    @abc.abstractmethod
    def connect(self):
        """Connect to the KBE server."""
        pass

    @abc.abstractmethod
    def send(self, data: bytes):
        """Send data to the server."""
        pass

    @abc.abstractmethod
    def close(self):
        """Close the active connection."""
        pass


class AppConnection(IConnection):
    """A connection to a KBE component."""
    
    def __init__(self, host: str, port: int, client_app: client.Client):
        self._host = host
        self._port = port
        self._client = client_app

        self._tcp_client = None  # type: tcpclient.TCPClient

        self._stream = None  # type: iostream.IOStream
        self._handle_stream_task = None  # type: asyncio.Future

        self._stopping = False  # type: bool
        self._closed = True  # type: bool
        logger.debug('[%s] Initialized', self)

    async def connect(self):
        self._tcp_client = tcpclient.TCPClient()
        self._stream = await self._tcp_client.connect(self._host, self._port,
                                                      timeout=5)
        self._start_handle_stream()
        self._closed = False
        logger.debug('[%s] Connected', self)

    async def send(self, data: bytes):
        await self._stream.write(data)
        logger.debug('[%s] Data has been sent', self)

    def close(self):
        logger.debug('[%s]  Close', self)
        if self._closed:
            return
        self._stopping = True
        self._stream.close()
        self._tcp_client.close()
        self._tcp_client = None
        self._handle_stream_task.cancel()
        self._handle_stream_task = None
        self._stopping = False
        self._closed = True
        logger.debug('[%s] Closed', self)

    def _start_handle_stream(self):
        """Handle incoming data."""

        async def forever():
            # TODO: (28 нояб. 2020 г. 20:55:10 burov_alexey@mail.ru)
            # Нужно отслеживать инфорацию посередине. Динамически по
            # длине высчитывать конец следующего сообщения (65535)
            try:
                while True:
                    data = await self._stream.read_bytes(65535, partial=True)
                    self._client.on_receive_data(data)
            except iostream.StreamClosedError as err:
                if self._stopping:
                    logger.info(f'[{self}] {err}')
                else:
                    # TODO: [05.12.2020 17:06 a.burov@mednote.life]
                    # Need reconnect
                    logger.error(f'[{self}] The connection has been closed by '
                                 f'the server: {err}')
            except Exception as err:
                logger.error(err, exc_info=True)

            raise KeyboardInterrupt

        self._handle_stream_task = asyncio.ensure_future(forever())

    def __str__(self):
        return f'{self.__class__.__name__}({self._host}, {self._port})'
