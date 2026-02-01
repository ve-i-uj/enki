"""Компонент частично повторяющий функционал KBEngine-компонента Loginapp."""

from __future__ import annotations

import abc
import asyncio
import logging
from asyncio import Future
from typing import TYPE_CHECKING, Generic, TypeAlias, TypeVar

from enki import msgspec
from enki.kbeenum import ComponentType
from enki.kbetype.decoders.custom_decoders import (
    KBEComponentType,
)
from enki.kbetype.pytypes.basic_data_types import KBEString
from enki.misc import devonly
from enki.misc.result import Result
from enki.misc.startable import IStartable
from enki.msg.imsg import IMsgBackChannel, IServerMsgReceiver
from enki.msg.message import Message
from enki.msg.msg_server import (
    TCPMsgBackChannel,
    TCPMsgServer,
)
from enki.msg_parser.client_msg_parser.client_msg_pasrser import (
    OnHelloCBParsedMsgData,
)
from enki.msg_parser.machine_msg_parser import (
    OnBroadcastInterfaceParsedMsgData,
)
from enki.msgspec import (
    get_comp_msg_specs,
)
from enki.net.addr import Addr

if TYPE_CHECKING:
    from enki.msg.msg_descr import (
        CompenentMsgSpecs,
        ComponentMsgSpecById,
    )

logger = logging.getLogger(__name__)

ComponentInfo: TypeAlias = OnBroadcastInterfaceParsedMsgData


class Loginapp(IStartable, IServerMsgReceiver):
    """Компонент частично повторяющий функционал KBEngine-компонента Loginapp."""

    def __init__(self, tcp_addr: Addr) -> None:
        """Конструктор KBEngine-компонента Loginapp.

        Args:
            tcp_addr (ComponentAddr): адрес приёма TCP-подключений

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        self._server_is_running: Future[None] | None = None

        self._tcp_addr = Addr(tcp_addr.ip_addr, tcp_addr.port)

        msg_spec_by_id: ComponentMsgSpecById = get_comp_msg_specs(
            ComponentType.LOGINAPP
        )
        comp_msg_specs: CompenentMsgSpecs = {
            ComponentType.CLIENT: get_comp_msg_specs(ComponentType.CLIENT)
        }
        # Сервер для обслуживания соединений.
        self._tcp_server = TCPMsgServer(
            self._tcp_addr,
            msg_spec_by_id,
            msg_receiver=self,
            comp_msg_specs=comp_msg_specs,
        )

        # Обработчики сообщений
        self._handlers: dict[int, _LoginappHandler] = {
            msgspec.loginapp.hello.id: _HelloHandler(self),
        }

        logger.info("[%s] Initialized", self)

    @property
    def tcp_addr(self) -> Addr:
        return self._tcp_addr

    async def wait_until_stop(self) -> None:
        """Ожидание, когда сервер завершит работу.

        Returns:
            Future: фюче-объект, показывающий работает ли серевер

        """
        if self._server_is_running is None:
            return

        await self._server_is_running

    async def start(self) -> Result:
        """Запустить компонент Супервизор.

        Returns:
            Result: результат запуска компонента

        """
        logger.debug("[%s] ", self)
        res = await self._tcp_server.start()
        if not res.success:
            return res

        # Переменная, что сервер запущен
        self._server_is_running = Future()

        logger.info("[%s] Started", self)
        return Result(success=True, result=None)

    def stop(self) -> None:
        """Остановить компонент."""
        if not self.is_started:
            return

        self._tcp_server.stop()

        if self._server_is_running is not None:
            self._server_is_running.set_result(None)

    @property
    def is_started(self) -> bool:
        """Флаг запущен ли Супервизор.

        Returns:
            bool: Флаг запущен ли Супервизор

        """
        return (
            self._server_is_running is not None
            and not self._server_is_running.done()
        )

    def on_receive_msg(
        self, msg: Message, back_channel: IMsgBackChannel
    ) -> None:
        """Колбэк на полученное сообщение.

        Args:
            msg (Message): полученное сервером сообщение
            back_channel (IMsgBackChannel): канал обратной связи

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        handler = self._handlers.get(msg.id)
        if handler is None:
            logger.warning(
                "[%s] There is no handler for the message %s", self, msg.id
            )
            return

        asyncio.create_task(handler.handle(msg, back_channel))  # noqa: RUF006

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"


_T_IMsgBackChannel = TypeVar("_T_IMsgBackChannel", bound=IMsgBackChannel)


class _LoginappHandler(abc.ABC, Generic[_T_IMsgBackChannel]):
    """Абстрактный класс для обработчика сообщения компонента Loginapp."""

    def __init__(self, app: Loginapp) -> None:
        self._app = app

    @abc.abstractmethod
    async def handle(
        self, msg: Message, back_channel: _T_IMsgBackChannel
    ) -> None:
        """Обработать сообщение."""

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    __repr__ = __str__


class _HelloHandler(_LoginappHandler[TCPMsgBackChannel]):
    """Обработчик для сообщения Loginapp::hello.

    Используется для проверки живой компонент или нет.
    """

    async def handle(
        self, msg: Message, back_channel: TCPMsgBackChannel
    ) -> None:
        """Обработать сообщение Loginapp::hello.

        Args:
            msg (Message): сообщение Loginapp::hello
            back_channel (TCPMsgBackChannel): канал обратной связи

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        pd = OnHelloCBParsedMsgData(
            kbe_version=KBEString("2.5.10"),
            assets_version=KBEString("0.1.0"),
            protocol_md5=KBEString("6615F2367124A5E4B390207ACC4906B6"),
            entity_def_md5=KBEString("06E15F102B481ACF8CA19E2F410D1B64"),
            componentType=KBEComponentType(ComponentType.LOGINAPP.value),
        )
        resp_msg = Message.create(msgspec.client.onHelloCB, pd.get_values())
        await back_channel.send_msg(resp_msg)
