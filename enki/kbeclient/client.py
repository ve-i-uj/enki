"""Client of a KBEngine server."""

from __future__ import annotations
import asyncio
import logging
from typing import Optional

from enki import interface
from enki.misc import devonly

from . import connection, serializer, message

logger = logging.getLogger(__name__)


class _DefaultMsgReceiver(interface.IMsgReceiver):
    """Message receiver using by default after initialization of the client."""

    def on_receive_msg(self, msg: interface.IMessage) -> bool:
        logger.debug(f'[{self}] ({devonly.func_args_values()})')
        return True

    def on_end_receive_msg(self):
        pass


class Client(interface.IClient, connection.IDataReceiver):
    """Client of a KBEngine server."""

    def __init__(self, addr: interface.AppAddr):
        self._addr = addr
        self._conn: Optional[connection.AppConnection] = None
        self._serializer = serializer.Serializer()
        self._msg_receiver = _DefaultMsgReceiver()

        self._in_buffer = b''

    @property
    def is_started(self) -> bool:
        return self._conn is not None

    @property
    def is_stopped(self) -> bool:
        return self._conn is None

    def set_msg_receiver(self, receiver: interface.IMsgReceiver):
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

            logger.debug('[%s] Message "%s" fields: %s', self, msg.name, msg.get_values())
            self._msg_receiver.on_receive_msg(msg)
            self._in_buffer = b''

    def on_end_receive_data(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._msg_receiver.on_end_receive_msg()
        asyncio.ensure_future(self.stop())

    async def send(self, msg: message.Message) -> None:
        logger.debug(f'[{self}]  ({devonly.func_args_values()})')
        assert self._conn is not None
        data = self._serializer.serialize(msg)
        await self._conn.send(data)

    async def start(self) -> None:
        await self._connect()

    async def stop(self):
        if self._conn is None:
            logger.warning(f'[{self}] The connection "{self._conn}" has '
                           f'already stopped')
            return
        self._conn.close()
        self._conn = None

    async def _connect(self):
        assert self._conn is None
        self._conn = connection.AppConnection(
            host=self._addr.host, port=self._addr.port, data_receiver=self
        )
        await self._conn.connect()

    def __str__(self) -> str:
        return f'{__class__.__name__}({self._addr})'
