"""Client of a KBEngine server."""

from __future__ import annotations

import abc
import logging
from typing import Optional

from enki import devonly
from enki.enkitype import Result, AppAddr
from enki.net.kbeclient.message import IMessage, Message, IMsgReceiver
from enki.net.kbeclient.connection import IDataReceiver, ConnectResult, AppConnection
from enki.net.kbeclient.serializer import MessageSerializer

logger = logging.getLogger(__name__)


class _DefaultMsgReceiver(IMsgReceiver):
    """Message receiver using by default after initialization of the client."""

    def on_receive_msg(self, msg: Message) -> bool:
        logger.debug(f'[{self}] ({devonly.func_args_values()})')
        return True

    def on_end_receive_msg(self):
        pass


class ClientResult(Result):
    success: bool
    result = None
    text: str = ''


class IClient(abc.ABC):

    @property
    @abc.abstractmethod
    def is_started(self) -> bool:
        pass

    @property
    @abc.abstractmethod
    def is_stopped(self) -> bool:
        pass

    @abc.abstractmethod
    def set_msg_receiver(self, receiver: IMsgReceiver) -> None:
        """Set the receiver of message."""
        pass

    @abc.abstractmethod
    async def send(self, msg: IMessage) -> None:
        """Send the message."""
        pass

    @abc.abstractmethod
    def start(self) -> Result:
        """Start this client."""
        pass

    @abc.abstractmethod
    def stop(self) -> None:
        """Stop this client."""
        pass


class Client(IClient, IDataReceiver):
    """Client of a KBEngine server."""

    def __init__(self, addr: AppAddr):
        self._addr = addr
        self._conn: Optional[AppConnection] = None
        self._serializer = MessageSerializer()
        self._msg_receiver = _DefaultMsgReceiver()

        self._in_buffer = b''

    @property
    def is_started(self) -> bool:
        return self._conn is not None

    @property
    def is_stopped(self) -> bool:
        return self._conn is None

    def set_msg_receiver(self, receiver: IMsgReceiver):
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
        self.stop()
        self._msg_receiver.on_end_receive_msg()

    async def send(self, msg: Message) -> None:
        logger.debug(f'[{self}]  ({devonly.func_args_values()})')
        assert self._conn is not None
        data = self._serializer.serialize(msg)
        await self._conn.send(data)

    async def start(self) -> ConnectResult:
        return (await self._connect())

    def stop(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        if self._conn is None:
            logger.debug(f'[{self}] The connection "{self._conn}" has '
                         f'already stopped')
            return
        self._conn.close()
        self._conn = None

    async def _connect(self) -> ConnectResult:
        assert self._conn is None
        self._conn = AppConnection(
            host=self._addr.host, port=self._addr.port, data_receiver=self
        )
        return (await self._conn.connect())

    def __str__(self) -> str:
        return f'{__class__.__name__}({self._addr})'
