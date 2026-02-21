"""Компонент частично повторяющий функционал KBEngine-компонента Baseapp."""

from __future__ import annotations

import abc
import asyncio
import logging
from asyncio import Future
from typing import TYPE_CHECKING, Generic, TypeVar

from enki import msgspec
from enki.kbeenum import ComponentType, ServerError
from enki.kbetype.decoders.basic_data_type_decoders import BLOB, STRING
from enki.kbetype.decoders.custom_decoders import KBEComponentType
from enki.kbetype.pytypes.basic_data_types import KBEBlob, KBEString, KBEUInt16
from enki.misc import devonly
from enki.misc.result import Result
from enki.misc.startable import IStartable
from enki.msg.imsg import IMsgBackChannel, IServerMsgReceiver
from enki.msg.message import Message
from enki.msg.msg_serializer import get_serializer
from enki.msg.msg_server import (
    TCPMsgBackChannel,
    TCPMsgServer,
)
from enki.msg_parser.baseapp_msg_parser import LoginBaseappMsgParser
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


class BaseappMock(IStartable, IServerMsgReceiver):
    """Компонент частично повторяющий функционал KBEngine-компонента Baseapp."""

    def __init__(self, tcp_addr: Addr, kbe_version: KBEString) -> None:
        """Конструктор KBEngine-компонента Baseapp.

        Args:
            tcp_addr (ComponentAddr): адрес приёма TCP-подключений

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        self._server_is_running: Future[None] | None = None

        self._tcp_addr = Addr(tcp_addr.ip_addr, tcp_addr.port)

        msg_spec_by_id: ComponentMsgSpecById = get_comp_msg_specs(
            ComponentType.BASEAPP
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
        self._handlers: dict[int, _BaseappHandler] = {
            msgspec.baseapp.loginBaseapp.id: _BaseappLoginBaseappHandler(self),
        }

        logger.info("[%s] Initialized", self)

        self._kbe_version = kbe_version
        self._assets_version = KBEString("0.1.0")
        self._protocol_md5 = KBEString("6615F2367124A5E4B390207ACC4906B6")
        self._entity_def_md5 = KBEString("06E15F102B481ACF8CA19E2F410D1B64")
        self._componentType = KBEComponentType(ComponentType.BASEAPP.value)

    @property
    def kbe_version(self) -> KBEString:
        """Получить версию ассетов."""
        return self._kbe_version

    @property
    def assets_version(self) -> KBEString:
        """Получить версию ассетов."""
        return self._assets_version

    @property
    def protocol_md5(self) -> KBEString:
        """Получить MD5 протокола."""
        return self._protocol_md5

    @protocol_md5.setter
    def protocol_md5(self, value: KBEString) -> None:
        """Установить MD5 протокола."""
        self._protocol_md5 = value

    @property
    def entity_def_md5(self) -> KBEString:
        """Получить MD5 определений сущностей."""
        return self._entity_def_md5

    @entity_def_md5.setter
    def entity_def_md5(self, value: KBEString) -> None:
        """Установить MD5 определений сущностей."""
        self._entity_def_md5 = value

    @property
    def componentType(self) -> KBEComponentType:
        """Получить тип компонента (только чтение)."""
        return self._componentType

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
        """Запустить компонент Baseapp.

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
        """Флаг запущен ли Baseapp.

        Returns:
            bool: Флаг запущен ли Baseapp

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


class _BaseappHandler(abc.ABC, Generic[_T_IMsgBackChannel]):
    """Абстрактный класс для обработчика сообщения компонента Baseapp."""

    def __init__(self, app: BaseappMock) -> None:
        self._app = app

    @abc.abstractmethod
    async def handle(
        self, msg: Message, back_channel: _T_IMsgBackChannel
    ) -> None:
        """Обработать сообщение."""

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    __repr__ = __str__


class _BaseappLoginBaseappHandler(_BaseappHandler[TCPMsgBackChannel]):
    """Обработчик для сообщения Baseapp::loginBaseapp."""

    def __init__(self, app: BaseappMock) -> None:
        self._app = app

    async def handle(
        self, msg: Message, back_channel: TCPMsgBackChannel
    ) -> None:
        """Обработать сообщение Baseapp::loginBaseapp.

        Args:
            msg (Message): сообщение Baseapp::loginBaseapp
            back_channel (TCPMsgBackChannel): канал обратной связи

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        # Парсим входящее сообщение
        req_res = LoginBaseappMsgParser().parse(msg)
        if not req_res.success:
            logger.warning(
                "[%s] The message '%s' is not parsed. Reason: '%s'",
                msg,
                self,
                req_res.text,
            )
            return

        req_pd = req_res.result
        assert req_pd is not None

        # Валидация данных
        if not req_pd.account_name:
            logger.debug(
                "[%s] Account name cannot be empty (client = %s)",
                self,
                back_channel.conn_info.client_addr,
            )

            # Формируем данные для ответа
            data = b""
            data += STRING.encode(KBEString(""))
            data += BLOB.encode(KBEBlob(b""))

            resp_msg = Message.create(
                msgspec.client.onLoginBaseappFailed,
                (
                    KBEUInt16(ServerError.NAME.value),  # Код ошибки
                    KBEBlob(data),  # Данные ответа
                ),
            )
            await back_channel.send_msg(resp_msg)
            return

        # Успешный логин
        logger.info(
            "[%s] Account '%s' logged in successfully to Baseapp",
            self,
            req_pd.account_name,
        )

        serializer = get_serializer(ComponentType.CLIENT)

        # Дальше посыпятся onUpdatePropertys и onCreatedProxies (и другие, если
        # сразу в мире появляется)

        # В KBEngine сперва отправляется onUpdatePropertys
        data = b"\xff\x01\x0e\x00\xf3\x00\x00\x00\x00\x04\x02\x00\x00\x00\x00\x00\x00\x00\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00"
        onUpdatePropertys_msg = serializer.deserialize(memoryview(data))[0]
        assert onUpdatePropertys_msg is not None

        await back_channel.send_msg(onUpdatePropertys_msg)

        data = b"\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00"
        onCreatedProxies_msg = serializer.deserialize(memoryview(data))[0]
        assert onCreatedProxies_msg is not None

        await back_channel.send_msg(onCreatedProxies_msg)


    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    __repr__ = __str__
