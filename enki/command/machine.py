"""Команды для компонента Machine."""

from __future__ import annotations

import asyncio
import logging
from asyncio import Future
from dataclasses import dataclass
from typing import Any, final, override

from enki import msgspec
from enki.kbeenum import ComponentType
from enki.kbetype.decoders.custom_decoders import (
    KBEComponentId,
    KBEComponentType,
    KBEIntAddr,
    KBEIntPort,
    KBEUid_,
    KBEUsername,
)
from enki.misc import devonly
from enki.msg.imsg import IServerMsgReceiver
from enki.msg.message import Message
from enki.msg.msg_client import RawRespUdpMsgClient, UdpMsgClient
from enki.msg.msg_server import UDPMsgBackChannel, UDPMsgServer
from enki.msg_parser.machine_msg_parser import (
    OnBroadcastInterfaceParsedMsgData,
    OnFindInterfaceAddrParsedMsgData,
    QueryComponentIDParsedMsgData,
)
from enki.net.addr import Addr, Port
from enki.settings import SECOND

from .icommand import CommandResult, ICommand

logger = logging.getLogger(__name__)


@dataclass
class OnQueryAllInterfaceInfosCommandResultData:
    """Данные результата команды Machine::onQueryAllInterfaceInfos.

    Содержит список описаний компонентов, полученных из ответных сообщений
    Machine::onBroadcastInterface. В ответ на Machine::onQueryAllInterfaceInfos
    отправляются байты с данными сообщения Machine::onBroadcastInterface
    (по одному сообщению на каждый зарегистрированный компонент).
    """

    infos: list[OnBroadcastInterfaceParsedMsgData]


@dataclass(frozen=True)
class OnQueryAllInterfaceInfosCommandResult(CommandResult):
    """Результат выполнения команды OnQueryAllInterfaceInfosCommand."""

    success: bool
    result: OnQueryAllInterfaceInfosCommandResultData | None = None
    text: str = ""


@final
class OnQueryAllInterfaceInfosCommand(ICommand[OnQueryAllInterfaceInfosCommandResult]):
    """Запросить информацию о всех зарегистрированных компонентах.

    Отправляет Machine::onQueryAllInterfaceInfos и собирает все ответные
    сообщения Machine::onBroadcastInterface в течение короткого таймаута.

    В KBEngine если uid != 0, то Machine будет делать фильтрацию по uid;
    username в фильтрации компонентов не участвует. Данная команда всегда
    использует uid = 0, т.е. фильтрация не применяется.
    """

    def __init__(
        self,
        machine_addr: Addr,
    ) -> None:
        """Конструктор команды.

        Args:
            machine_addr (Addr): адрес компонента Machine, у которого
                запрашивается информация о компонентах

        """
        self._machine_addr = machine_addr

    @override
    async def execute(self) -> OnQueryAllInterfaceInfosCommandResult:
        """Выполнить команду.

        Отправляет запрос и собирает все пришедшие ответы
        Machine::onBroadcastInterface в течение таймаута.

        Returns:
            OnQueryAllInterfaceInfosCommandResult: результат выполнения;
                при ошибке отправки запроса возвращается с success=False
                и текстом ошибки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values = (
            KBEUid_(0),
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
            infos.append(OnBroadcastInterfaceParsedMsgData(*resp_values))

        return OnQueryAllInterfaceInfosCommandResult(
            success=True,
            result=OnQueryAllInterfaceInfosCommandResultData(infos),
        )


@dataclass
class QueryComponentIDCommandResultData(QueryComponentIDParsedMsgData):
    """Данные результата команды Machine::queryComponentID.

    Представляют собой разобранное ответное сообщение
    Machine::queryComponentID с вычисленным componentID.
    """


@dataclass(frozen=True)
class QueryComponentIDCommandResult(CommandResult):
    """Результат выполнения команды QueryComponentIDCommand."""

    success: bool
    result: QueryComponentIDCommandResultData | None = None
    text: str = ""


@final
class QueryComponentIDCommand(ICommand[QueryComponentIDCommandResult]):
    """Команда для запроса Machine::queryComponentID.

    В ответ Machine вычисляет componentID и передаёт его обратно
    UDP-сообщением. Способ доставки ответа зависит от ``cb_port``:

    - если ``cb_port`` не задан (порт "нет порта"), ответ ожидается на том же
      клиентском UDP-сокете, с которого был отправлен запрос;
    - если ``cb_port`` задан, на этом порту поднимается временный UDP-сервер,
      и ответ принимается на него. Адрес для ответа - это источник запроса.
    """

    def __init__(self, addr: Addr, cb_port: Port) -> None:
        """Конструктор команды, отправляющей Machine::queryComponentID.

        Args:
            addr (Addr): адрес компонента Machine, который ответит на сообщение
            cb_port (Port): UDP-порт, на который отправится ответная дейтаграмма;
                если порт не задан, ответ ожидается на клиентском UDP-сокете

        """
        self._addr = addr
        self._cb_port = cb_port

    @override
    async def execute(self) -> QueryComponentIDCommandResult:
        """Выполнить команду.

        Returns:
            QueryComponentIDCommandResult: результат выполнения; при отсутствии
                ответа или ошибке возвращается с success=False

        """
        pd = QueryComponentIDParsedMsgData.get_empty()
        pd.finderRecvPort = KBEIntPort(self._cb_port)

        msg = Message.create(msgspec.machine.queryComponentID, pd.get_values())

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
            _ = await resp_awaitable_client.send_msg(msg)
            resp_msg = await resp_awaitable_client.wait_only_first_resp_msg(
                0.5 * SECOND
            )
            if resp_msg is None:
                text = f"[{self}] The message cannot be sent ({msg})"
                logger.warning(text)
                return QueryComponentIDCommandResult(success=False)

            values: tuple[Any, ...] = resp_msg.get_values()
            resp_pd = QueryComponentIDCommandResultData(*values)

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
            """Приёмник сообщений для серверного компонента.

            По первому полученному сообщению заполняет переданный Future
            результатом, что позволяет ожидать ответ асинхронно.
            """

            def __init__(self, cb_future: Future[Message]) -> None:
                """Конструктор приёмника.

                Args:
                    cb_future (Future[Message]): future, в который
                        устанавливается первое полученное сообщение

                """
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
        _ = await client.send_msg(msg)

        timeout = 1.0 * SECOND
        try:
            resp_msg_from_server = await asyncio.wait_for(resp_future, timeout)
        except TimeoutError:
            text = f'There is no response from the server "{self._addr}"'
            logger.warning(text)
            return QueryComponentIDCommandResult(success=False)
        finally:
            server.stop()

        logger.info(
            "[%s] The response has been received (resp_msg = %s)",
            self,
            resp_msg_from_server,
        )

        values_from_server: tuple[Any, ...] = resp_msg_from_server.get_values()
        resp_pd = QueryComponentIDCommandResultData(*values_from_server)
        return QueryComponentIDCommandResult(success=True, result=resp_pd)


@dataclass
class OnFindInterfaceAddrCommandResultData(OnBroadcastInterfaceParsedMsgData):
    """Данные результата команды Machine::onFindInterfaceAddr.

    Содержат разобранное ответное сообщение Machine::onBroadcastInterface,
    описывающее найденный компонент. Набор полей совпадает с родительским
    классом.
    """


@dataclass(frozen=True)
class OnFindInterfaceAddrCommandResult(CommandResult):
    """Результат выполнения команды OnFindInterfaceAddrCommand."""

    success: bool
    result: OnFindInterfaceAddrCommandResultData | None = None
    text: str = ""


@final
class OnFindInterfaceAddrCommand(ICommand[OnFindInterfaceAddrCommandResult]):
    """Команда для запроса по UDP Machine::onFindInterfaceAddr.

    Позволяет найти адрес интерфейса конкретного компонента по его типу
    и (опционально) id. В ответ Machine присылает сообщение
    Machine::onBroadcastInterface с описанием найденного компонента.
    """

    def __init__(
        self,
        machine_addr: Addr,
        uid: int,
        username: str,
        find_component_type: ComponentType,
        find_component_id: int = 0,
    ) -> None:
        """Конструктор команды.

        Args:
            machine_addr (Addr): адрес компонента Machine
            uid (int): uid аккаунта для фильтрации (0 - без фильтрации)
            username (str): имя пользователя (в фильтрации не участвует)
            find_component_type (ComponentType): тип искомого компонента
            find_component_id (int): id искомого компонента (0 - любой
                компонент указанного типа)

        """
        self._machine_addr = machine_addr
        self._uid = uid
        self._username = username
        self._find_component_type = find_component_type
        self._find_component_id = find_component_id

    @override
    async def execute(self) -> OnFindInterfaceAddrCommandResult:
        """Выполнить команду.

        Отправляет запрос Machine::onFindInterfaceAddr и ожидает первое
        ответное сообщение Machine::onBroadcastInterface.

        Returns:
            OnFindInterfaceAddrCommandResult: результат выполнения; при
                отсутствии ответа возвращается с success=False

        """
        req_pd = OnFindInterfaceAddrParsedMsgData(
            uid=KBEUid_(self._uid),
            username=KBEUsername(self._username),
            # Запрашивающий компонент это, вроде.
            componentType=KBEComponentType(ComponentType.UNKNOWN_COMPONENT),
            componentID=KBEComponentId(self._find_component_id),
            findComponentType=KBEComponentType(self._find_component_type.value),
            finderAddr=KBEIntAddr(0),
            finderRecvPort=KBEIntPort(0),
        )
        msg = Message.create(msgspec.machine.onFindInterfaceAddr, req_pd.get_values())
        client = RawRespUdpMsgClient(
            self._machine_addr,
            msgspec.machine.onBroadcastInterface,
        )
        await client.send_msg(msg)

        resp_msg = await client.wait_only_first_resp_msg(0.5 * SECOND)
        if resp_msg is None:
            return OnFindInterfaceAddrCommandResult(success=False)

        resp_values: tuple[Any, ...] = resp_msg.get_values()
        resp_pd = OnFindInterfaceAddrCommandResultData(*resp_values)

        return OnFindInterfaceAddrCommandResult(success=True, result=resp_pd)
