"""TCPClient of a KBEngine server."""

from __future__ import annotations

import abc
import asyncio
import logging
from typing import Optional

from enki.misc import devonly
from enki.core.enkitype import Result, AppAddr
from enki.core import msgspec
from enki.core.message import Message, MsgDescr
from enki.net.inet import IClientMsgReceiver
from enki.net.connection import TCPClientConnection
from enki.core.message import MessageSerializer

from .inet import IClientDataReceiver, ITCPClient

logger = logging.getLogger(__name__)


class _DefaultMsgReceiver(IClientMsgReceiver):
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


class TCPClient(ITCPClient, IClientDataReceiver):
    """TCPClient of a KBEngine server."""

    def __init__(self, addr: AppAddr, msg_spec_by_id: dict[int, MsgDescr]):
        self._addr = addr
        self._conn: Optional[TCPClientConnection] = None
        self._serializer = MessageSerializer(msg_spec_by_id)
        self._msg_receiver = _DefaultMsgReceiver()

        self._in_buffer = b''

    @property
    def is_alive(self) -> bool:
        return self._conn is not None

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

    async def send_msg(self, msg: Message) -> None:
        logger.debug(f'[{self}]  ({devonly.func_args_values()})')
        assert self._conn is not None
        data = self._serializer.serialize(msg)
        await self._conn.send(data)

    async def send_msg_content(self, msg: Message) -> bool:
        assert False, 'TODO'
        return False

    async def start(self) -> Result:
        assert self._conn is None
        self._conn = TCPClientConnection(self._addr, self)
        return (await self._conn.connect())

    def stop(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        if self._conn is None:
            logger.debug(f'[{self}] The connection "{self._conn}" has '
                         f'already stopped')
            return
        self._conn.close()
        self._conn = None

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
