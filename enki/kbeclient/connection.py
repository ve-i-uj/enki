"""Different connections to the KBEngine server."""

from __future__ import annotations
import abc
import asyncio
import logging
from typing import Optional

from tornado import tcpclient
from tornado import iostream
from enki import exception

from enki.misc import runutil

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


class IDataReceiver(abc.ABC):

    @abc.abstractmethod
    def on_receive_data(self, data: memoryview) -> None:
        """Handle incoming bytes data from the server."""
        pass

    @abc.abstractmethod
    def on_end_receive_data(self):
        """No more data after this callback called."""
        pass


class AppConnection(IConnection):
    """The connection to a KBE component."""

    def __init__(self, host: str, port: int, data_receiver: IDataReceiver):
        self._host: str = host
        self._port: int = port
        self._data_receiver = data_receiver

        self._tcp_client: Optional[tcpclient.TCPClient] = None
        self._stream: Optional[iostream.IOStream] = None
        self._handling_stream_task: Optional[asyncio.Future] = None

        self._stopping: bool = False
        self._closed: bool = True
        logger.debug('[%s] Initialized', self)

    async def connect(self):
        self._tcp_client = tcpclient.TCPClient()
        # TODO: [31.07.2021 burov_alexey@mail.ru]:
        # Таймаут из константы или настроек
        self._stream = await self._tcp_client.connect(self._host, self._port,
                                                      timeout=5)
        self._start_handle_stream()
        self._closed = False
        logger.debug('[%s] Connected', self)

    async def send(self, data: bytes):
        assert self._stream is not None
        await self._stream.write(data)
        logger.debug('[%s] Data has been sent', self)

    def close(self):
        logger.debug('[%s]  Close', self)
        if self._closed:
            return
        assert self._stream is not None and self._tcp_client is not None \
            and self._handling_stream_task is not None
        self._stopping = True
        self._stream.close()
        self._tcp_client.close()
        self._tcp_client = None
        self._handling_stream_task.cancel()
        self._handling_stream_task = None
        self._stopping = False
        self._closed = True
        logger.debug('[%s] Closed', self)

    def _start_handle_stream(self):
        """Handle incoming data."""

        async def forever():
            # TODO: (28 нояб. 2020 г. 20:55:10 burov_alexey@mail.ru)
            # Нужно отслеживать информацию посередине. Динамически по
            # длине высчитывать конец следующего сообщения (65535)
            assert self._stream is not None
            try:
                while True:
                    # TODO: [2022-08-26 13:12 burov_alexey@mail.ru]:
                    # Это скорей всего настройка из пропускного канала BaseApp
                    # что-то такое видел. Можно текстовым поиском по кбе проекту поисать
                    data = await self._stream.read_bytes(65535, partial=True)
                    data = memoryview(data)
                    self._data_receiver.on_receive_data(data)
            except iostream.StreamClosedError as err:
                if self._stopping:
                    logger.info(f'[{self}] {err}')
                    return
                logger.error(f'[{self}] The connection has been closed by the server: {err}')
                # To finilize the instance in the next tick
                self._data_receiver.on_end_receive_data()

        self._handling_stream_task = asyncio.ensure_future(forever())

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self._host}, {self._port})'
