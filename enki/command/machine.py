"""Команды для компонента Machine."""

from __future__ import annotations

import asyncio
import logging
from asyncio import Future
from dataclasses import dataclass
from typing import Any

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
from enki.msg.imsg import IServerMsgReceiver
from enki.msg.message import Message
from enki.msg.msg_client import RawRespUdpMsgClient, UdpMsgClient
from enki.msg.msg_server import UDPMsgBackChannel, UDPMsgServer
from enki.msg_parser.machine_msg_parser import (
    OnBroadcastInterfaceParsedData,
    OnFindInterfaceAddrParsedData,
    QueryComponentIDParsedMsgData,
)
from enki.net.addr import Addr, Port
from enki.settings import SECOND

from .icommand import CommandResult, ICommand

logger = logging.getLogger(__name__)


@dataclass
class OnQueryAllInterfaceInfosCommandResponseData:
    """Ответ на Machine::onQueryAllInterfaceInfos.

    В ответ на Machine::onQueryAllInterfaceInfos отправляются байты с данными
    сообщения Machine::onBroadcastInterface.
    """

    infos: list[OnBroadcastInterfaceParsedData]


@dataclass
class OnQueryAllInterfaceInfosCommandResult(CommandResult):
    """Результат выполнения команды по получению информации о компонентах."""

    success: bool
    result: OnQueryAllInterfaceInfosCommandResponseData | None = None
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
            success=True,
            result=OnQueryAllInterfaceInfosCommandResponseData(infos),
        )


@dataclass
class QueryComponentIDCommandResponseData(QueryComponentIDParsedMsgData):
    """Ответ на Machine::queryComponentID."""


@dataclass
class QueryComponentIDCommandResult(CommandResult):
    """Результат выполнения команды по запросу id от компонента."""

    success: bool
    result: QueryComponentIDCommandResponseData | None = None
    text: str = ""


class QueryComponentIDCommand(ICommand):
    """Команда для запроса Machine::queryComponentID.

    В ответ вычисляется componentID и передаётся обратно UDP сообщением
    Machine::queryComponentID без обёртки на порт из поля finderRecvPort.
    Адрес для ответа - это источник запроса.
    """

    def __init__(self, addr: Addr, cb_port: Port) -> None:
        """Конструктор команды, отправляющей Machine::queryComponentID.

        Args:
            addr (Addr): адрес компонента Machine, который ответит на сообщение
            cb_port (Port): UDP-порт, на который отправится ответная дейтаграмма

        """
        self._addr = addr
        self._cb_port = cb_port

    async def execute(self) -> QueryComponentIDCommandResult:
        """Выполнить команду.

        Returns:
            QueryComponentIDParserMsgResult: Объект результата команды

        """
        pd = QueryComponentIDParsedMsgData.get_empty()
        pd.finderRecvPort = KBEIntPort(self._cb_port)

        msg = Message.create(msgspec.machine.queryComponentID, pd.values())

        if self._cb_port.is_no_port():
            logger.info(
                (
                    "[%s] The callback port is '0'. Waiting for the response on "
                    "the client udp-socket"
                ),
                self,
            )
            # Значит ответ будет на клиентский UDP-сокет
            resp_awaitable_client = RawRespUdpMsgClient(
                self._addr, msgspec.machine.queryComponentID
            )
            await resp_awaitable_client.send_msg(msg)
            resp_msg = await resp_awaitable_client.wait_only_first_resp_msg(
                0.5 * SECOND
            )
            if resp_msg is None:
                text = f"[{self}] The message cannot be sent ({msg})"
                logger.warning(text)
                return QueryComponentIDCommandResult(success=False)

            values: tuple[Any, ...] = resp_msg.get_values()
            resp_pd = QueryComponentIDCommandResponseData(*values)

            logger.info(
                (
                    "[%s] The response has been received (resp_msg = %s, new "
                    "component id = '%s')"
                ),
                self,
                resp_msg,
                resp_pd.componentID,
            )

            return QueryComponentIDCommandResult(success=True, result=resp_pd)

        # Под приём ответа будет запущен UDP-сервер

        class ServerMsgReceiver(IServerMsgReceiver[UDPMsgBackChannel]):
            """Приёмник сообщений для серверного компонента."""

            def __init__(self, cb_future: Future[Message]):
                self._cb_future = cb_future

            def on_receive_msg(
                self, msg: Message, back_channel: UDPMsgBackChannel
            ) -> None:
                """Колбэк на полученное сообщение.

                Args:
                    msg (Message): полученное сервером сообщение
                    back_channel (IMsgBackChannel): канал обратной связи

                """
                if not self._cb_future.done():
                    self._cb_future.set_result(msg)

        resp_future: Future[Message] = Future()
        cb_addr = Addr.create_default_gw_addr(self._cb_port)
        server = UDPMsgServer(
            cb_addr,
            ComponentType.MACHINE,
            msg_receiver=ServerMsgReceiver(resp_future),
        )
        res = await server.start()
        if not res.success:
            text = (
                f"[{self}] There is no response for the message '{msg}' "
                f"(cb_addr = {cb_addr}, reason = {res.text})"
            )
            logger.warning(text)
            return QueryComponentIDCommandResult(success=False)

        # Сервер запущен, теперь отправим сообщение и будем ждать ответ

        client = UdpMsgClient(self._addr, ComponentType.MACHINE)
        await client.send_msg(msg)

        timeout = 1.0 * SECOND
        try:
            resp_msg_from_server = await asyncio.wait_for(resp_future, timeout)
        except TimeoutError:
            text = f'There is no response from the server "{self._addr}"'
            logger.warning(text)
            return QueryComponentIDCommandResult(success=False)

        logger.info(
            "[%s] The response has been received (resp_msg = %s)",
            self,
            resp_msg_from_server,
        )

        values_from_server: tuple[Any, ...] = resp_msg_from_server.get_values()
        resp_pd = QueryComponentIDCommandResponseData(*values_from_server)
        return QueryComponentIDCommandResult(success=True, result=resp_pd)


@dataclass
class OnFindInterfaceAddrCommandResponseData(OnBroadcastInterfaceParsedData):
    """Ответ на Machine::onFindInterfaceAddr.

    В ответ на Machine::onFindInterfaceAddr отправляются байты с данными
    сообщения Machine::onBroadcastInterface.

    Поля теже, что и родительского класса.
    """


@dataclass
class OnFindInterfaceAddrCommandResult(CommandResult):
    """Результат команды Machine::onFindInterfaceAddr."""

    success: bool
    result: OnFindInterfaceAddrCommandResponseData | None = None
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
        resp_pd = OnFindInterfaceAddrCommandResponseData(*resp_values)

        return OnFindInterfaceAddrCommandResult(success=True, result=resp_pd)
