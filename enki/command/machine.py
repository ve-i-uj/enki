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
from enki.core import kbeenum, utils
from enki.core import msgspec
from enki.core.message import Message, MessageSerializer
from enki.net.client import UDPClient
from enki.net import server
from enki.net.server import UDPServer
from enki.handler.serverhandler import machinehandler
from enki.handler.serverhandler.machinehandler import OnBroadcastInterfaceHandlerResult, OnBroadcastInterfaceParsedData, QueryComponentIDHandlerResult, \
    QueryComponentIDParsedData, OnFindInterfaceAddrHandler, OnFindInterfaceAddrParsedData

from ._base import ICommand, CommandResult
from .common import RequestCommand


logger = logging.getLogger(__name__)


@dataclass
class OnQueryAllInterfaceInfosCommandResultData:
    """Ответ на Machine::onQueryAllInterfaceInfos."""
    infos: list[OnBroadcastInterfaceParsedData]


@dataclass
class OnQueryAllInterfaceInfosCommandResult(CommandResult):
    success: bool
    result: OnQueryAllInterfaceInfosCommandResultData
    text: str = ''

    def get_info(self, component_type: kbeenum.ComponentType
                 ) -> list[OnBroadcastInterfaceParsedData]:
        res = []
        for info in self.result.infos:
            if info.component_type == component_type:
                res.append(info)
        return res


class OnQueryAllInterfaceInfosCommand(ICommand):
    """Machine command 'OnQueryAllInterfaceInfos'."""

    def __init__(self, addr: AppAddr, uid: int = 0, username: str = 'root',
                 finderRecvPort: int = 0):
        """Запросить информацию о всех зарегестрированных компонентах.

        Если uid != 0, то KBE Machine будет делать фильтрацию по uid; username
        в фильтрации компонентов не участвует.
        """
        self._addr = addr
        self._req_msg = Message(
            spec=msgspec.app.machine.onQueryAllInterfaceInfos,
            fields=(uid, username, finderRecvPort)
        )

    async def execute(self) -> OnQueryAllInterfaceInfosCommandResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        req_cmd = RequestCommand(
            self._addr, self._req_msg, msgspec.app.machine.onBroadcastInterface
        )
        res = await req_cmd.execute()
        if not res.success:
            return OnQueryAllInterfaceInfosCommandResult(
                False, OnQueryAllInterfaceInfosCommandResultData([]), res.text
            )

        infos = []
        for msg in res.result:
            infos.append(OnBroadcastInterfaceParsedData(*msg.get_values()))
        return OnQueryAllInterfaceInfosCommandResult(
            True, OnQueryAllInterfaceInfosCommandResultData(infos)
        )


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


@dataclass
class OnFindInterfaceAddrUDPCommandResult(CommandResult):
    success: bool
    result: Optional[OnBroadcastInterfaceParsedData]
    text: str = ''


class OnFindInterfaceAddrUDPCommand(ICommand):
    """Команда для запроса по UDP Machine::onFindInterfaceAddr."""

    def __init__(self, addr: AppAddr, pd: OnFindInterfaceAddrParsedData):
        self._addr = addr
        self._client = UDPClient(addr)
        self._pd = pd

    async def execute(self) -> OnFindInterfaceAddrUDPCommandResult:
        self._msg = Message(msgspec.app.machine.onFindInterfaceAddr, self._pd.values())
        serializer = MessageSerializer(msgspec.app.machine.SPEC_BY_ID)
        data = serializer.serialize(self._msg)

        # Запуск колбэк сервера для ответа
        cb_addr = self._pd.callback_address
        cb_future: Future[Optional[bytes]] = asyncio.get_running_loop().create_future()
        cb_server = UDPCallbackServer(cb_addr, cb_future)
        res = await cb_server.start()
        if not res.success:
            return OnFindInterfaceAddrUDPCommandResult(False, None, res.text)

        await self._client.send(data)

        try:
            data = await asyncio.wait_for(cb_future, timeout=settings.CONNECT_TO_SERVER_TIMEOUT)
        except asyncio.TimeoutError:
            return OnFindInterfaceAddrUDPCommandResult(
                False, None, f'There is no response from the server "{self._addr}"'
            )
        if data is None:
            return OnFindInterfaceAddrUDPCommandResult(
                False, None, f'The data hasn`t been sent to the server "{self._addr}"'
            )
        logger.info('[%s] The response has been received', self)

        msg, _ = serializer.deserialize_only_data(
            data, msgspec.app.machine.onBroadcastInterface
        )
        if msg is None:
            return OnFindInterfaceAddrUDPCommandResult(
                False, None, f'The data is mailformed. It cannot be deserialized'
            )
        pd = OnBroadcastInterfaceParsedData(*msg.get_values())
        return OnFindInterfaceAddrUDPCommandResult(True, pd)



@dataclass
class OnFindInterfaceAddrTCPCommandResultData:
    """Ответ на Machine::onQueryAllInterfaceInfos."""
    infos: list[OnBroadcastInterfaceParsedData]


@dataclass
class OnFindInterfaceAddrTCPCommandResult(CommandResult):
    success: bool
    result: OnFindInterfaceAddrTCPCommandResultData
    text: str = ''


class OnFindInterfaceAddrTCPCommand(ICommand):
    """Команда для запроса по TCP Machine::onFindInterfaceAddr."""

    def __init__(self, addr: AppAddr, pd: OnFindInterfaceAddrParsedData):
        self._addr = addr
        assert pd.addr == 0 and pd.finderRecvPort == 0, \
            'The TCP connection doesn`t need callback address'
        self._pd = pd

    async def execute(self) -> OnFindInterfaceAddrTCPCommandResult:
        req_msg = Message(msgspec.app.machine.onFindInterfaceAddr, self._pd.values())
        request_cmd = RequestCommand(
            self._addr, req_msg, msgspec.app.machine.onBroadcastInterface
        )
        res = await request_cmd.execute()
        if not res.success:
            return OnFindInterfaceAddrTCPCommandResult(
                False, OnFindInterfaceAddrTCPCommandResultData([]), res.text
            )

        infos = []
        for msg in res.result:
            infos.append(OnBroadcastInterfaceParsedData(*msg.get_values()))
        return OnFindInterfaceAddrTCPCommandResult(
            True, OnFindInterfaceAddrTCPCommandResultData(infos)
        )
