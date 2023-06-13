import asyncio
from asyncio import Future
from dataclasses import dataclass
import logging
import time
from typing import Any

from enki import settings
from enki.core import utils
from enki.misc import devonly
from enki.core.enkitype import AppAddr, Result
from enki.core.message import Message, MsgDescr
from enki.net.client import TCPClient

from ._base import ICommand

logger = logging.getLogger(__name__)


@dataclass
class RequestCommandResult:
    success: bool
    result: list[Message]
    text: str = ''


class RequestCommand(ICommand):
    """Команда для одноразового запроса на сервер.

    Запрос совершается через TCP соединение.
    """

    def __init__(self, addr: AppAddr, req_msg: Message, resp_msg_spec: MsgDescr,
                 timeout=settings.WAITING_FOR_SERVER_TIMEOUT,
                 stop_on_first_data_chunk=False):
        self._client = TCPClient(addr, on_receive_data=self.on_receive_data)
        self._req_msg = req_msg
        self._resp_msg_spec = resp_msg_spec
        self._timeout = timeout
        self._stop_on_first_data_chunk = stop_on_first_data_chunk

        self._response_msgs: list[Message] = []

    def on_receive_data(self, data: bytes):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        serializer = utils.get_serializer_for(
            self._resp_msg_spec.component_type)
        msg, data_tail = serializer.deserialize_only_data(
            data, self._resp_msg_spec)
        assert msg is not None
        if data_tail:
            logger.warning('[%s] Not all data has been deserialized (data_tail=%s)',
                           self, data_tail.tobytes())
        self._response_msgs.append(msg)
        if self._stop_on_first_data_chunk:
            self._client.stop()

    async def execute(self) -> RequestCommandResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        res = await self._client.start()
        if not res.success:
            return RequestCommandResult(False, [], res.text)
        serializer = utils.get_serializer_for(
            self._req_msg.spec.component_type)
        data = serializer.serialize(self._req_msg)
        success = await self._client.send(data)
        if not success:
            return RequestCommandResult(False, [], 'The data hasn`t been sent (see log)')

        timeout_time = time.time() + self._timeout
        while timeout_time > time.time() and self._client.is_alive:
            await asyncio.sleep(settings.GAME_TICK)

        if not self._client.is_alive and not self._response_msgs:
            # Соединение закрыто, ответа не было
            return RequestCommandResult(
                False, [],
                f'The server closed the connection (message = "{self._req_msg}")'
            )

        if not self._response_msgs:
            # По таймауту цикл завершился. Ответ так и не прислали, состояние
            # соединения не имеет значения.
            self._client.stop()
            return RequestCommandResult(False, [], f'No response for the message "{self._req_msg}"')

        # Есть ответ от сервера
        self._client.stop()
        res = self._response_msgs

        return RequestCommandResult(True, res)
