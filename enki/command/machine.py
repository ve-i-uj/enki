"""Commands for sending messages to Machine."""

from __future__ import annotations
import asyncio

import logging
import time
from asyncio import Future
from dataclasses import dataclass
from typing import Optional

from enki import settings
from enki.misc import devonly
from enki.core.enkitype import AppAddr
from enki.core import kbeenum
from enki.core import msgspec
from enki.core.message import Message, MessageSerializer
from enki.net.client import StreamClient, UDPClient
from enki.net import server
from enki.net.server import UDPServer
from enki.handler.serverhandler import machinehandler
from enki.handler.serverhandler.machinehandler import QueryComponentIDHandlerResult, QueryComponentIDParsedData

from . import _base
from ._base import StreamCommand, ICommand
from .common import LookAppCommand


logger = logging.getLogger(__name__)


@dataclass
class OnQueryAllInterfaceInfosCommandResultData:
    """Ответ на Machine::onQueryAllInterfaceInfos."""
    infos: list[machinehandler.OnBroadcastInterfaceParsedData]


@dataclass
class OnQueryAllInterfaceInfosCommandResult(_base.CommandResult):
    success: bool
    result: OnQueryAllInterfaceInfosCommandResultData
    text: str = ''

    def get_info(self, component_type: kbeenum.ComponentType
                 ) -> list[machinehandler.OnBroadcastInterfaceParsedData]:
        res = []
        for info in self.result.infos:
            if info.component_type == component_type:
                res.append(info)
        return res


class OnQueryAllInterfaceInfosCommand(StreamCommand):
    """Machine command 'OnQueryAllInterfaceInfos'."""

    def __init__(self, client: StreamClient, uid: int, username: str,
                 finderRecvPort: int = 0):
        super().__init__(client)
        self._client = client
        self._client.set_resp_msg_spec(
            msgspec.app.machine.onBroadcastInterface
        )

        self._req_msg_spec = msgspec.app.machine.onQueryAllInterfaceInfos
        self._success_resp_msg_spec = msgspec.app.machine.onBroadcastInterface
        self._error_resp_msg_specs = []

        self._msg = Message(
            spec=self._req_msg_spec,
            fields=(uid, username, finderRecvPort)
        )

    async def execute(self) -> OnQueryAllInterfaceInfosCommandResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        await self._client.send_msg(self._msg)
        infos = []
        # На это сообщение сервер будет удерживать соединение, поэтому закроем
        # его сами. А о том, что ответ закончился узнаем только после закрытия.
        timeout_time = time.time() + settings.SECOND * 2
        while timeout_time > time.time():
            if self.last_chunk_time + settings.SECOND > time.time():
                # Давно уже ничего не отправляется, значит закончилась передача
                break
            await asyncio.sleep(settings.SECOND * 0.5)
        self._client.stop()
        for info in (await self.get_result()):
            infos.append(machinehandler.OnBroadcastInterfaceParsedData(*info))
        return OnQueryAllInterfaceInfosCommandResult(
            True, OnQueryAllInterfaceInfosCommandResultData(infos)
        )


class MachineLookAppCommand(LookAppCommand):
    """Machine command 'lookApp'."""

    def __init__(self, client: StreamClient):
        super().__init__(client, msgspec.app.machine.lookApp,
                         msgspec.app.machine.fakeRespLookApp)


class UDPCallbackServer(UDPServer):

    def __init__(self, addr: AppAddr, cb_future: Future[Optional[bytes]]):
        super().__init__(addr)
        self._cb_future = cb_future

    async def on_receive_data(self, data: memoryview, addr: AppAddr):
        self._cb_future.set_result(data.tobytes())

    def on_stop_receive(self):
        super().on_stop_receive()
        self._cb_future.set_result(None)


class QueryComponentIDCommand(ICommand):
    """Команда для запроса Machine::queryComponentID."""

    def __init__(self, addr: AppAddr, pd: QueryComponentIDParsedData):
        self._addr = addr
        self._client = UDPClient(addr)
        self._pd = pd

    async def execute(self) -> QueryComponentIDHandlerResult:
        self._msg = Message(msgspec.app.machine.queryComponentID, self._pd.values())
        serializer = MessageSerializer(msgspec.app.machine.SPEC_BY_ID)
        data = serializer.serialize(self._msg)

        # Запуск колбэк сервера для ответа
        cb_port = self._pd.callback_port
        cb_future: Future[Optional[bytes]] = asyncio.get_running_loop().create_future()
        cb_server = UDPCallbackServer(AppAddr('0.0.0.0', cb_port), cb_future)
        res = await cb_server.start()
        if not res.success:
            return QueryComponentIDHandlerResult(False, None, res.text)

        await self._client.send(data)

        try:
            data = await asyncio.wait_for(cb_future, timeout=settings.CONNECT_TO_SERVER_TIMEOUT)
        except asyncio.TimeoutError:
            return QueryComponentIDHandlerResult(
                False, None, f'There is no response from the server "{self._addr}"'
            )
        if data is None:
            return QueryComponentIDHandlerResult(
                False, None, f'The data hasn`t been sent to the server "{self._addr}"'
            )
        logger.info('[%s] The response has been received', self)

        msg, _ = serializer.deserialize_only_data(
            data, msgspec.app.machine.queryComponentID
        )
        if msg is None:
            return QueryComponentIDHandlerResult(
                False, None, f'The data is mailformed. It cannot be deserialized'
            )
        pd = QueryComponentIDParsedData(*msg.get_values())
        return QueryComponentIDHandlerResult(True, pd)
