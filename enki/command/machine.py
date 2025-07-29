"""Команды для компонента Machine."""

from __future__ import annotations

import asyncio
import logging
from asyncio import Future
from dataclasses import dataclass

from enki import kbeenum, msgspec, settings
from enki.core import kbemath
from enki.kbetype import KBEUid
from enki.kbetype.decoders.custom_decoders import KBEIntPort, KBEUsername
from enki.misc import devonly
from enki.msg.message import Message
from enki.msg_parser.machine_msg_parser import (
    OnBroadcastInterfaceParsedData,
    OnQueryAllInterfaceInfosResponseData,
)
from enki.net.addr import Addr
from enki.net.server import UDPServer, get_free_port

from .icommand import CommandResult, ICommand

logger = logging.getLogger(__name__)


# def get_info(
#     self, component_type: kbeenum.ComponentType
# ) -> list[OnBroadcastInterfaceParsedData]:
#     res = []
#     for info in self.result.infos:
#         if info.component_type == component_type:
#             res.append(info)
#     return res


@dataclass
class OnQueryAllInterfaceInfosCommandResult(CommandResult):
    """Результат выполнения команды по получению информации о компонентах."""

    success: bool
    result: OnQueryAllInterfaceInfosResponseData
    text: str = ""


class OnQueryAllInterfaceInfosCommand(ICommand):
    """Запросить информацию о всех зарегестрированных компонентах.

    В KBEngine если uid != 0, то KBE Machine будет делать фильтрацию по uid;
    username в фильтрации компонентов не участвует.
    """

    def __init__(
        self,
        machine_addr: Addr,
    ) -> None:
        """Конструктор команды.

        Args:
            machine_addr (Addr): адрес компонента Machine

        """
        self._addr = machine_addr

    async def execute(self) -> OnQueryAllInterfaceInfosCommandResult:
        """Выполнить команду.

        Returns:
            OnQueryAllInterfaceInfosCommandResult: результат выполнения

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        free_port = get_free_port()
        values = (
            KBEUid(0),
            KBEUsername(""),
            KBEIntPort(kbemath.port2int(free_port)),
        )
        msg = Message.create(msgspec.machine.onQueryAllInterfaceInfos, values)

        # server =

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
    def __init__(self, addr: Addr, cb_future: Future[bytes] | None):
        super().__init__(addr)
        self._cb_future = cb_future

    async def on_receive_data(self, data: memoryview, addr: Addr):
        self._cb_future.set_result(data.tobytes())

    def on_stop_receive(self):
        super().on_stop_receive()
        self._cb_future.set_result(None)


class QueryComponentIDCommand(ICommand):
    """Команда для запроса Machine::queryComponentID."""

    def __init__(self, addr: Addr, pd: QueryComponentIDParsedData):
        self._addr = addr
        self._client = UDPClient(addr)
        self._pd = pd

    async def execute(self) -> QueryComponentIDMsgResult:
        self._msg = Message(
            msgspec.app.machine.queryComponentID, self._pd.values()
        )
        serializer = MessageEncoder(msgspec.app.machine.SPEC_BY_ID)
        data = serializer.serialize(self._msg)

        # Запуск колбэк сервера для ответа
        cb_port = self._pd.callback_port
        cb_future: Future[bytes] | None = (
            asyncio.get_running_loop().create_future()
        )
        cb_server = UDPCallbackServer(Addr("0.0.0.0", cb_port), cb_future)
        res = await cb_server.start()
        if not res.success:
            return QueryComponentIDMsgResult(False, None, res.text)

        await self._client.send_data(data)

        try:
            data = await asyncio.wait_for(
                cb_future, timeout=settings.CONNECT_TO_SERVER_TIMEOUT
            )
        except asyncio.TimeoutError:
            return QueryComponentIDMsgResult(
                False,
                None,
                f'There is no response from the server "{self._addr}"',
            )
        if data is None:
            return QueryComponentIDMsgResult(
                False,
                None,
                f'The data hasn`t been sent to the server "{self._addr}"',
            )
        logger.info("[%s] The response has been received", self)

        msg, _ = serializer.deserialize_only_data(
            data, msgspec.app.machine.queryComponentID
        )
        if msg is None:
            return QueryComponentIDMsgResult(
                False,
                None,
                f"The data is mailformed. It cannot be deserialized",
            )
        pd = QueryComponentIDParsedData(*msg.get_values())
        return QueryComponentIDMsgResult(True, pd)


@dataclass
class OnFindInterfaceAddrUDPCommandResult(CommandResult):
    success: bool
    result: OnBroadcastInterfaceParsedData | None
    text: str = ""


class OnFindInterfaceAddrUDPCommand(ICommand):
    """Команда для запроса по UDP Machine::onFindInterfaceAddr."""

    def __init__(self, addr: Addr, pd: OnFindInterfaceAddrParsedData):
        self._addr = addr
        self._client = UDPClient(addr)
        self._pd = pd

    async def execute(self) -> OnFindInterfaceAddrUDPCommandResult:
        self._msg = Message(
            msgspec.app.machine.onFindInterfaceAddr, self._pd.values()
        )
        serializer = MessageEncoder(msgspec.app.machine.SPEC_BY_ID)
        data = serializer.serialize(self._msg)

        # Запуск колбэк сервера для ответа
        cb_addr = self._pd.callback_address
        cb_future: Future[bytes] | None = (
            asyncio.get_running_loop().create_future()
        )
        cb_server = UDPCallbackServer(cb_addr, cb_future)
        res = await cb_server.start()
        if not res.success:
            return OnFindInterfaceAddrUDPCommandResult(False, None, res.text)

        await self._client.send_data(data)

        try:
            data = await asyncio.wait_for(
                cb_future, timeout=settings.CONNECT_TO_SERVER_TIMEOUT
            )
        except asyncio.TimeoutError:
            return OnFindInterfaceAddrUDPCommandResult(
                False,
                None,
                f'There is no response from the server "{self._addr}"',
            )
        if data is None:
            return OnFindInterfaceAddrUDPCommandResult(
                False,
                None,
                f'The data hasn`t been sent to the server "{self._addr}"',
            )
        cb_server.stop()
        logger.info("[%s] The response has been received", self)

        msg, _ = serializer.deserialize_only_data(
            data, msgspec.app.machine.onBroadcastInterface
        )
        if msg is None:
            return OnFindInterfaceAddrUDPCommandResult(
                False,
                None,
                f"The data is mailformed. It cannot be deserialized",
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
    text: str = ""


class OnFindInterfaceAddrTCPCommand(ICommand):
    """Команда для запроса по TCP Machine::onFindInterfaceAddr."""

    def __init__(self, addr: Addr, pd: OnFindInterfaceAddrParsedData):
        self._addr = addr
        assert pd.addr == 0 and pd.finderRecvPort == 0, (
            "The TCP connection doesn`t need callback address"
        )
        self._pd = pd

    async def execute(self) -> OnFindInterfaceAddrTCPCommandResult:
        req_msg = Message(
            msgspec.app.machine.onFindInterfaceAddr, self._pd.values()
        )
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
