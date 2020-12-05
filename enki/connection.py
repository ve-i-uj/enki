"""Different connections to the KBEngine server."""

import abc
import asyncio
import logging

from tornado import tcpclient
from tornado import iostream

from enki import datahandler, message, serializer
from enki.misc import devonly

logger = logging.getLogger(__name__)


class IConnection(abc.ABC):

    @abc.abstractmethod
    def connect(self):
        """Connect to the KBE server."""
        pass

    @abc.abstractmethod
    def send(self, msg: message.Message):
        """Send a message to the server."""
        pass

    @abc.abstractmethod
    def close(self):
        """Close the active connection."""
        pass


class LoginAppConnection(IConnection):
    """A connection to LoginApp."""
    
    def __init__(self, host: str, port: int, serializer_: serializer.Serializer,
                 handler: datahandler.IncomingDataHandler):
        self._host = host
        self._port = port
        self._serializer = serializer_
        self._handler = handler

        self._tcp_client = tcpclient.TCPClient()

        self._stream: iostream.IOStream = None
        self._handle_stream_task = None

        self._stopping = False
        logger.debug('[%s] Initialized', self)

    async def connect(self):
        self._stream = await self._tcp_client.connect(self._host, self._port)
        await self._start_handle_stream()
        logger.debug('[%s] Connected', self)

    async def send(self, msg: message.Message):
        logger.debug('[%s] Sending a message ... (%s)', self, devonly.func_args_values())
        data = self._serializer.serialize(msg)
        await self._stream.write(data)
        logger.debug('[%s] The message "%s" has been sent', self, msg)

    def close(self):
        self._stopping = True
        self._stream.close()
        logger.debug('[%s] Closed', self)

    async def _start_handle_stream(self):
        """Handle incoming data."""

        async def forever():
            try:
                while True:
                    # TODO: (28 нояб. 2020 г. 20:55:10 burov_alexey@mail.ru)
                    # Нужно отслеживать инфорацию посередине. Динамически по
                    # длине высчитывать конец следующего сообщения
                    data = await self._stream.read_bytes(65535, partial=True)
                    self._handler.handle(data)
            except iostream.StreamClosedError as e:
                if self._stopping:
                    logger.info(f'[{self}] {e}')
                else:
                    # TODO: [05.12.2020 17:06 a.burov@mednote.life]
                    # Need reconnect
                    logger.error(f'[{self}] The connection has been closed by '
                                 f'the server: {e}')

        self._handle_stream_task = asyncio.ensure_future(forever())

    def __str__(self):
        return f'{self.__class__.__name__}({self._host}, {self._port})'
