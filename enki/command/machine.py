"""Команды для компонента Machine."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from enki import msgspec
from enki.kbeenum import ComponentType
from enki.kbetype import KBEUid
from enki.kbetype.decoders.custom_decoders import (
    KBEComponentId,
    KBEComponentType,
    KBEIntAddr,
    KBEIntPort,
    KBEUsername,
)
from enki.misc import devonly
from enki.msg.message import Message
from enki.msg.msg_client import RawRespUdpMsgClient
from enki.msg_parser.machine_msg_parser import (
    OnBroadcastInterfaceParsedData,
    OnFindInterfaceAddrParsedData,
    OnFindInterfaceAddrResponseData,
    OnQueryAllInterfaceInfosResponseData,
)
from enki.net.addr import Port
from enki.settings import SECOND

from .icommand import CommandResult, ICommand

if TYPE_CHECKING:
    from enki.net.addr import Addr

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
    result: OnQueryAllInterfaceInfosResponseData | None = None
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
        self._machine_addr = machine_addr

    async def execute(self) -> OnQueryAllInterfaceInfosCommandResult:
        """Выполнить команду.

        Returns:
            OnQueryAllInterfaceInfosCommandResult: результат выполнения

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values = (
            KBEUid(0),
            KBEUsername(""),
            KBEIntPort(Port.get_no_port_obj()),
        )
        msg = Message.create(msgspec.machine.onQueryAllInterfaceInfos, values)

        client = RawRespUdpMsgClient(
            self._machine_addr, msgspec.machine.onBroadcastInterface
        )

        success = await client.send_msg(msg)
        if not success:
            text = f"[{self}] The message cannot be sent ({msg})"
            logger.warning(text)
            return OnQueryAllInterfaceInfosCommandResult(success=False, text=text)

        infos = []
        resp_msg: Message
        async for resp_msg in client.wait_and_iterate_resp_msgs(0.5 * SECOND):
            resp_values: tuple[Any, ...] = resp_msg.get_values()
            infos.append(OnBroadcastInterfaceParsedData(*resp_values))

        return OnQueryAllInterfaceInfosCommandResult(
            success=True, result=OnQueryAllInterfaceInfosResponseData(infos)
        )


# class UDPCallbackServer(UDPServer):
#     def __init__(self, addr: Addr, cb_future: Future[bytes] | None):
#         super().__init__(addr)
#         self._cb_future = cb_future

#     async def on_receive_data(self, data: memoryview, addr: Addr):
#         self._cb_future.set_result(data.tobytes())

#     def on_stop_receive(self):
#         super().on_stop_receive()
#         self._cb_future.set_result(None)


# class QueryComponentIDCommand(ICommand):
#     """Команда для запроса Machine::queryComponentID."""

#     def __init__(self, addr: Addr, pd: QueryComponentIDParsedData):
#         self._addr = addr
#         self._client = UDPClient(addr)
#         self._pd = pd

#     async def execute(self) -> QueryComponentIDMsgResult:
#         self._msg = Message(
#             msgspec.app.machine.queryComponentID, self._pd.values()
#         )
#         serializer = MessageEncoder(msgspec.app.machine.SPEC_BY_ID)
#         data = serializer.serialize(self._msg)

#         # Запуск колбэк сервера для ответа
#         cb_port = self._pd.callback_port
#         cb_future: Future[bytes] | None = (
#             asyncio.get_running_loop().create_future()
#         )
#         cb_server = UDPCallbackServer(Addr("0.0.0.0", cb_port), cb_future)
#         res = await cb_server.start()
#         if not res.success:
#             return QueryComponentIDMsgResult(False, None, res.text)

#         await self._client.send_data(data)

#         try:
#             data = await asyncio.wait_for(
#                 cb_future, timeout=settings.CONNECT_TO_SERVER_TIMEOUT
#             )
#         except asyncio.TimeoutError:
#             return QueryComponentIDMsgResult(
#                 False,
#                 None,
#                 f'There is no response from the server "{self._addr}"',
#             )
#         if data is None:
#             return QueryComponentIDMsgResult(
#                 False,
#                 None,
#                 f'The data hasn`t been sent to the server "{self._addr}"',
#             )
#         logger.info("[%s] The response has been received", self)

#         msg, _ = serializer.deserialize_only_data(
#             data, msgspec.app.machine.queryComponentID
#         )
#         if msg is None:
#             return QueryComponentIDMsgResult(
#                 False,
#                 None,
#                 f"The data is mailformed. It cannot be deserialized",
#             )
#         pd = QueryComponentIDParsedData(*msg.get_values())
#         return QueryComponentIDMsgResult(True, pd)


@dataclass
class OnFindInterfaceAddrCommandResult(CommandResult):
    """Результат команды Machine::onFindInterfaceAddr."""

    success: bool
    result: OnFindInterfaceAddrResponseData | None = None
    text: str = ""


class OnFindInterfaceAddrCommand(ICommand):
    """Команда для запроса по UDP Machine::onFindInterfaceAddr."""

    def __init__(
        self,
        machine_addr: Addr,
        uid: int,
        username: str,
        find_component_type: ComponentType,
        find_component_id: int = 0,
    ):
        """Конструктор команды.

        Args:
            machine_addr (Addr): _description_
            uid (int): _description_
            username (str): _description_
            find_component (ComponentType): _description_

        """
        self._machine_addr = machine_addr
        self._uid = uid
        self._username = username
        self._find_component_type = find_component_type
        self._find_component_id = find_component_id

    async def execute(self) -> OnFindInterfaceAddrCommandResult:
        """Выполнить команду."""
        req_pd = OnFindInterfaceAddrParsedData(
            uid=KBEUid(self._uid),
            username=KBEUsername(self._username),
            # Запрашивающий компонент это, вроде.
            componentType=KBEComponentType(ComponentType.UNKNOWN_COMPONENT),
            componentID=KBEComponentId(self._find_component_id),
            findComponentType=KBEComponentType(self._find_component_type.value),
            finderAddr=KBEIntAddr(0),
            finderRecvPort=KBEIntPort(0),
        )
        msg = Message.create(msgspec.machine.onFindInterfaceAddr, req_pd.values())
        client = RawRespUdpMsgClient(
            self._machine_addr,
            msgspec.machine.onBroadcastInterface,
        )
        await client.send_msg(msg)

        resp_msg = await client.wait_only_first_resp_msg(0.5 * SECOND)
        if resp_msg is None:
            return OnFindInterfaceAddrCommandResult(success=False)

        resp_values: tuple[Any, ...] = resp_msg.get_values()
        resp_pd = OnFindInterfaceAddrResponseData(*resp_values)

        return OnFindInterfaceAddrCommandResult(success=True, result=resp_pd)


# @dataclass
# class OnFindInterfaceAddrTCPCommandResultData:
#     """Ответ на Machine::onQueryAllInterfaceInfos."""

#     infos: list[OnBroadcastInterfaceParsedData]


# @dataclass
# class OnFindInterfaceAddrTCPCommandResult(CommandResult):
#     success: bool
#     result: OnFindInterfaceAddrTCPCommandResultData
#     text: str = ""


# class OnFindInterfaceAddrTCPCommand(ICommand):
#     """Команда для запроса по TCP Machine::onFindInterfaceAddr."""

#     def __init__(self, addr: Addr, pd: OnFindInterfaceAddrParsedData):
#         self._addr = addr
#         assert pd.addr == 0 and pd.finderRecvPort == 0, (
#             "The TCP connection doesn`t need callback address"
#         )
#         self._pd = pd

#     async def execute(self) -> OnFindInterfaceAddrTCPCommandResult:
#         req_msg = Message(
#             msgspec.app.machine.onFindInterfaceAddr, self._pd.values()
#         )
#         request_cmd = RequestCommand(
#             self._addr, req_msg, msgspec.app.machine.onBroadcastInterface
#         )
#         res = await request_cmd.execute()
#         if not res.success:
#             return OnFindInterfaceAddrTCPCommandResult(
#                 False, OnFindInterfaceAddrTCPCommandResultData([]), res.text
#             )

#         infos = []
#         for msg in res.result:
#             infos.append(OnBroadcastInterfaceParsedData(*msg.get_values()))
#         return OnFindInterfaceAddrTCPCommandResult(
#             True, OnFindInterfaceAddrTCPCommandResultData(infos)
#         )
